import os
import re
import json
import sqlite3
from dataclasses import dataclass
from typing import List, Optional, Tuple
from langchain_chroma import Chroma
import chromadb
from dotenv import load_dotenv
from langchain_upstage import UpstageEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document


# =========================
# Config
# =========================
load_dotenv()

UPSTAGE_API_KEY = os.getenv("UPSTAGE_API_KEY")
DB_NAME = os.getenv("DB_NAME", "card_gorilla_master_rank.db")

PERSIST_DIR = os.getenv("CHROMA_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("CHROMA_COLLECTION", "cards_top100_text")

TOP_N = int(os.getenv("TOP_N", "100"))
MODEL_NAME = os.getenv("EMBED_MODEL", "solar-embedding-1-large")

# 임베딩 품질/비용 균형: 너무 길면 노이즈 + 비용 증가
MAX_DOC_CHARS = int(os.getenv("MAX_DOC_CHARS", "3500"))

# 검색 기본값
DEFAULT_K = int(os.getenv("DEFAULT_K", "5"))


# =========================
# Utils
# =========================
def _require_api_key() -> str:
    if not UPSTAGE_API_KEY or not UPSTAGE_API_KEY.strip():
        raise RuntimeError(
            "UPSTAGE_API_KEY가 없습니다. .env에 UPSTAGE_API_KEY를 설정해 주세요.")
    return UPSTAGE_API_KEY.strip()


def _clean_text(s: str) -> str:
    """임베딩 품질을 위해 텍스트를 약간 정리"""
    s = s.replace("\u200b", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def _build_card_text(company: str, name: str, benefits_json: str, max_chars: int) -> Optional[str]:
    """
    benefits_json(list) -> 임베딩 대상 텍스트로 변환
    (사용자님 요청대로 'json 구조화'를 활용하지 않고, 원문 텍스트 기반)
    """
    try:
        benefit_list = json.loads(benefits_json)
        if not isinstance(benefit_list, list) or not benefit_list:
            return None
    except Exception:
        return None

    lines = [f"[{company}] {name}"]
    for b in benefit_list:
        if not isinstance(b, dict):
            continue
        title = str(b.get("title", "")).strip()
        detail = str(b.get("detail", "")).strip()
        if not title and not detail:
            continue
        # 너무 긴 detail은 줄여서 노이즈 방지
        if len(detail) > 200:
            detail = detail[:200] + "…"
        lines.append(f"- {title} {detail}".strip())

    text = "\n".join(lines)
    text = _clean_text(text)
    return text[:max_chars] if text else None


def _fetch_cards(db_name: str, top_n: int) -> List[Tuple[int, str, str, str, int]]:
    """
    반환: (gorilla_id, name, company, benefits_json, ranking)
    """
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT gorilla_id, name, company, benefits_json, ranking
        FROM cards
        WHERE ranking IS NOT NULL
          AND ranking <= ?
        ORDER BY ranking ASC
        """,
        (top_n,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


@dataclass
class CardHit:
    gorilla_id: int
    company: str
    name: str
    ranking: Optional[int]
    score: float
    preview: str


# =========================
# Vector Index
# =========================
class CardVectorIndex:
    def __init__(self, persist_dir: str, collection_name: str):
        _require_api_key()
        # self.persist_dir = persist_dir
        self.collection_name = collection_name

        self.embeddings = UpstageEmbeddings(
            api_key=UPSTAGE_API_KEY,
            model=MODEL_NAME,
        )

        self.client = chromadb.HttpClient(
            host="chroma.cocohwan.site",
            port=443,
            ssl=True
        )
        
        # 로드(없으면 빈 컬렉션 생성)
        self.store = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
        )

    # 서버 버전
    def reset_collection(self) -> None:
        """완전 재구축이 필요할 때 컬렉션을 삭제"""
        try:
            # 서버 모드에서는 client를 통해 직접 delete_collection 호출
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass

        # 삭제 후 다시 연결 (객체 재생성 불필요, 컬렉션만 다시 잡으면 됨)
        self.store = Chroma(
            client=self.client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
        )

    def build_or_update(self, top_n: int = TOP_N, rebuild: bool = False) -> int:
        """
        - rebuild=True면 컬렉션 삭제 후 전체 재적재
        - 기본은 동일 id로 upsert 느낌으로 "중복 없이" 넣기
        """
        if rebuild:
            self.reset_collection()

        cards = _fetch_cards(DB_NAME, top_n)
        documents: List[Document] = []
        ids: List[str] = []

        for (g_id, name, company, benefits_json, ranking) in cards:
            text = _build_card_text(
                company, name, benefits_json, MAX_DOC_CHARS)
            if not text:
                continue

            # Chroma id는 문자열이 안정적
            doc_id = f"card:{g_id}"

            doc = Document(
                page_content=text,
                metadata={
                    "gorilla_id": int(g_id),
                    "name": name,
                    "company": company,
                    "ranking": int(ranking) if ranking is not None else None,
                },
            )
            documents.append(doc)
            ids.append(doc_id)

        if not documents:
            print("⚠️ 적재할 문서가 없습니다. benefits_json 파싱 실패 또는 데이터가 비어있을 수 있습니다.")
            return 0

        # 중복 방지: 동일 ids로 add_documents를 호출하면 Chroma가 덮어쓰는 동작을 기대할 수 있으나
        # 버전/설정에 따라 다를 수 있어, 안전하게 기존 id 삭제 후 추가합니다.
        try:
            self.store.delete(ids=ids)
        except Exception:
            pass

        self.store.add_documents(documents=documents, ids=ids)

        print(f"🎉 벡터 DB 업데이트 완료: {len(documents)}개 (Server=chroma.cocohwan.site, collection={self.collection_name})")
        return len(documents)

    def search(self, query: str, k: int = DEFAULT_K, use_mmr: bool = True) -> List[CardHit]:
        """
        - use_mmr=True: 결과 다양성 증가(비슷한 카드만 몰리는 현상 완화)
        - 점수 포함 출력 위해 similarity_search_with_score 사용
        """
        query = _clean_text(query)

        if use_mmr:
            # 1. Get diverse documents using MMR
            #    fetch_k: 초기 유사도 검색을 위한 문서 수 (k의 3배로 설정)
            mmr_docs = self.store.max_marginal_relevance_search(query, k=k, fetch_k=k * 3)

            # 2. Get a larger pool of documents with their similarity scores
            #    이는 MMR로 선택된 문서들의 점수를 찾아 매칭하기 위함입니다.
            #    이 과정이 "깔끔하지만 비용이 증가합니다"에 해당합니다.
            scored_candidates_pool = self.store.similarity_search_with_relevance_scores(query, k=k * 3)
            
            # Create a map from gorilla_id to (document, score) for quick lookup
            scored_map = {doc.metadata.get("gorilla_id"): (doc, score) for doc, score in scored_candidates_pool}

            results = []
            for mmr_doc in mmr_docs:
                g_id = mmr_doc.metadata.get("gorilla_id")
                if g_id in scored_map:
                    # Use the document from the MMR search (for diversity),
                    # but its score from the similarity search pool.
                    results.append((mmr_doc, scored_map[g_id][1]))
            
            # Ensure only k results are returned, maintaining MMR's diverse order
            results = results[:k]
            
        else:
            results = self.store.similarity_search_with_score(query, k=k)

        hits: List[CardHit] = []
        for doc, score in results:
            md = doc.metadata or {}
            gid = int(md.get("gorilla_id", 0))
            company = str(md.get("company", ""))
            name = str(md.get("name", ""))
            ranking = md.get("ranking", None)

            # preview: 첫 번째 혜택 줄 일부
            lines = doc.page_content.splitlines()
            preview = ""
            if len(lines) >= 2:
                preview = lines[1][:80] + ("…" if len(lines[1]) > 80 else "")
            elif lines:
                preview = lines[0][:80] + ("…" if len(lines[0]) > 80 else "")

            hits.append(
                CardHit(
                    gorilla_id=gid,
                    company=company,
                    name=name,
                    ranking=int(ranking) if ranking is not None else None,
                    score=float(score),
                    preview=preview,
                )
            )
        return hits


# =========================
# CLI Demo
# =========================
def build_vector_db(rebuild: bool = False) -> None:
    index = CardVectorIndex(PERSIST_DIR, COLLECTION_NAME)
    index.build_or_update(top_n=TOP_N, rebuild=rebuild)


def recommend_card(query: str, k: int = 3) -> None:
    index = CardVectorIndex(PERSIST_DIR, COLLECTION_NAME)

    print(f"\n🔍 질문: '{query}'")
    print("-" * 60)

    hits = index.search(query, k=k, use_mmr=False)

    for i, h in enumerate(hits, 1):
        r = f"{h.ranking}위" if h.ranking is not None else "랭킹없음"
        print(f"[{i}위] ({r}) {h.company} - {h.name}")
        print(f"   점수(score): {h.score:.4f}")
        print(f"   💡 매칭 힌트: {h.preview}")
        print("-" * 60)


if __name__ == "__main__":
    # 1) 최초 1회 구축(또는 재구축 필요 시 rebuild=True)
    # build_vector_db(rebuild=True)

    # 2) 구축 후 추천 테스트
    recommend_card("일본 여행 갈 때 라운지 무료인 카드 추천해줘", k=5)
    recommend_card("스타벅스랑 점심값 할인 많이 되는 카드", k=3)
    pass

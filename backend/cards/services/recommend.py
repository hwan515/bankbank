import os
import re
from dataclasses import dataclass
from typing import List, Optional

from django.conf import settings


@dataclass
class CardHit:
    gorilla_id: int
    company: str
    name: str
    ranking: Optional[int]
    score: float
    preview: str


class CardRecommendService:
    """
    Chroma 벡터 DB를 활용한 카드 추천 서비스
    외부 Chroma 서버(https://chroma.cocohwan.site:443)에 연결
    """

    def __init__(self):
        self.api_key = getattr(settings, 'UPSTAGE_API_KEY', '') or os.getenv('UPSTAGE_API_KEY', '')

        # Chroma 서버 설정
        self.chroma_host = getattr(settings, 'CHROMA_HOST', None) or os.getenv(
            'CHROMA_HOST', 'chroma.cocohwan.site'
        )
        self.chroma_port = int(getattr(settings, 'CHROMA_PORT', None) or os.getenv(
            'CHROMA_PORT', '443'
        ))
        self.collection_name = getattr(settings, 'CHROMA_COLLECTION', None) or os.getenv(
            'CHROMA_COLLECTION', 'cards_top100_text'
        )
        self.model_name = os.getenv('EMBED_MODEL', 'solar-embedding-1-large')

        self._embeddings = None
        self._store = None

    @property
    def embeddings(self):
        if self._embeddings is None:
            from langchain_upstage import UpstageEmbeddings
            self._embeddings = UpstageEmbeddings(
                api_key=self.api_key,
                model=self.model_name,
            )
        return self._embeddings

    @property
    def store(self):
        if self._store is None:
            import chromadb
            from langchain_chroma import Chroma

            # HTTP 클라이언트로 외부 Chroma 서버에 연결
            chroma_client = chromadb.HttpClient(
                host=self.chroma_host,
                port=self.chroma_port,
                ssl=True,
            )

            self._store = Chroma(
                client=chroma_client,
                collection_name=self.collection_name,
                embedding_function=self.embeddings,
            )
        return self._store

    def _clean_text(self, s: str) -> str:
        s = s.replace("\u200b", " ")
        s = re.sub(r"[ \t]+", " ", s)
        s = re.sub(r"\n{3,}", "\n\n", s)
        return s.strip()

    def recommend(self, query: str, k: int = 5) -> List[CardHit]:
        """
        자연어 질의로 유사 카드 검색
        """
        query = self._clean_text(query)
        results = self.store.similarity_search_with_score(query, k=k)

        hits: List[CardHit] = []
        for doc, score in results:
            md = doc.metadata or {}
            gid = int(md.get("gorilla_id", 0))
            company = str(md.get("company", ""))
            name = str(md.get("name", ""))
            ranking = md.get("ranking")

            # preview 생성
            lines = doc.page_content.splitlines()
            preview = ""
            if len(lines) >= 2:
                preview = lines[1][:80] + ("..." if len(lines[1]) > 80 else "")
            elif lines:
                preview = lines[0][:80] + ("..." if len(lines[0]) > 80 else "")

            hits.append(CardHit(
                gorilla_id=gid,
                company=company,
                name=name,
                ranking=int(ranking) if ranking else None,
                score=float(score),
                preview=preview,
            ))

        return hits

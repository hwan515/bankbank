import logging
import os
import re
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)
from django.db.models import Q, F
from django.db.models.functions import Coalesce
from dotenv import load_dotenv

from cards.models import Card

# .env 파일 로드
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(PROJECT_ROOT / 'backend' / '.env')
load_dotenv(PROJECT_ROOT / 'analyze_card' / '.env')


@dataclass
class RecommendHit:
    """추천 결과 아이템"""
    gorilla_id: int
    score: float
    semantic_score: float
    fit_score: float
    preview: str
    reasons: List[str] = field(default_factory=list)

    # Chroma 메타데이터 (DB 조회 실패 시 fallback)
    name: str = ""
    company: str = ""
    ranking: Optional[int] = None


class CardRecommendService:
    """
    MySQL + Chroma 하이브리드 카드 추천 서비스

    흐름:
    1. MySQL에서 하드 필터(연회비, 전월실적 등)로 후보군 생성
    2. Chroma에서 자연어 쿼리로 의미 기반 검색
    3. 두 후보를 합치고 최종 점수화
    4. 추천 이유 생성
    """

    # 점수 가중치 (조정 가능)
    WEIGHT_SEMANTIC = 0.50
    WEIGHT_FIT = 0.50

    def __init__(self):
        # GMS API (OpenAI 호환)
        self.gms_api_key = os.getenv('GMS_KEY', '')
        self.chroma_host = getattr(settings, 'CHROMA_HOST', None) or os.getenv('CHROMA_HOST', 'chroma.cocohwan.site')
        self.chroma_port = int(getattr(settings, 'CHROMA_PORT', None) or os.getenv('CHROMA_PORT', '443'))
        self.collection_name = getattr(settings, 'CHROMA_COLLECTION', None) or os.getenv('CHROMA_COLLECTION', 'cards_top100_text')
        self.model_name = os.getenv('EMBED_MODEL', 'text-embedding-3-large')

        self._embeddings = None
        self._store = None

        self.chroma_top_n = int(os.getenv('RECOMMEND_CHROMA_TOP_N', '100'))
        self.sql_top_n = int(os.getenv('RECOMMEND_SQL_TOP_N', '200'))

    @property
    def embeddings(self):
        if self._embeddings is None:
            from langchain_openai import OpenAIEmbeddings
            self._embeddings = OpenAIEmbeddings(
                api_key=self.gms_api_key,
                base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1",
                model=self.model_name,
            )
        return self._embeddings

    @property
    def store(self):
        if self._store is None:
            import chromadb
            from langchain_chroma import Chroma

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

    def _get_sql_candidates(self, filters: Dict[str, Any]) -> List[int]:
        """MySQL에서 하드 필터로 후보 카드 gorilla_id 리스트 반환"""
        qs = Card.objects.all()

        company = (filters.get('company') or '').strip()
        if company:
            qs = qs.filter(company=company)

        card_type = (filters.get('card_type') or '').strip()
        if card_type in ('CRD', 'CHK'):
            qs = qs.filter(card_type=card_type)

        max_annual_fee = filters.get('max_annual_fee')
        if isinstance(max_annual_fee, int) and max_annual_fee > 0:
            qs = qs.filter(annual_fee_min__lte=max_annual_fee)

        max_min_spending = filters.get('max_min_spending')
        if isinstance(max_min_spending, int) and max_min_spending > 0:
            qs = qs.filter(min_spending__lte=max_min_spending)

        # 랭킹순으로 상위 N개만 (ranking이 None인 카드는 뒤로)
        # Coalesce로 None을 큰 숫자로 대체
        qs = qs.annotate(
            ranking_order=Coalesce('ranking', 999999)
        ).order_by('ranking_order', '-created_at')[:self.sql_top_n]

        return list(qs.values_list('gorilla_id', flat=True))

    def _get_chroma_candidates(self, query: str, filters: Dict[str, Any]) -> Dict[int, Dict[str, Any]]:
        """
        Chroma에서 의미 기반 검색
        반환: {gorilla_id: {'score': float, 'preview': str, 'metadata': dict}}
        """
        query = self._clean_text(query)
        if not query:
            return {}

        try:
            results = self.store.similarity_search_with_score(query, k=self.chroma_top_n)
        except Exception as e:
            logger.error(f"Chroma 검색 오류: {e}", exc_info=True)
            return {}

        candidates = {}
        for doc, distance in results:
            md = doc.metadata or {}
            gid = md.get('gorilla_id')
            if gid is None:
                continue
            gid = int(gid)

            # distance -> similarity score 변환 (코사인 거리 기준)
            # distance가 작을수록 유사도가 높음
            score = 1.0 / (1.0 + float(distance))

            # preview 생성
            lines = doc.page_content.splitlines()
            preview = ""
            if len(lines) >= 2:
                preview = lines[1][:100]
            elif lines:
                preview = lines[0][:100]
            if len(preview) > 80:
                preview = preview[:80] + "..."

            candidates[gid] = {
                'score': score,
                'preview': preview,
                'metadata': md,
            }

        return candidates

    def _calc_fit_score(self, card: Card, category_weights: Dict[str, float]) -> float:
        """사용자 선호 카테고리와 카드 혜택의 매칭 점수 계산"""
        if not category_weights or not card.categories:
            return 0.0

        score = 0.0
        for cat in card.categories:
            w = float(category_weights.get(cat, 0))
            score += w

        # 정규화 (0 ~ 1)
        denom = sum(float(v) for v in category_weights.values()) or 1.0
        return min(score / denom, 1.0)

    def _generate_reasons(self, card: Card, *args, **kwargs) -> List[str]:
        """
        추천 이유를 생성합니다. DB에서 조회한 가장 메인이 되는 혜택을 이유로 제시합니다.
        """
        reason = ""
        
        # 1순위: main_benefit 필드 (get_main_benefit_display() 등 모델의 요약 메소드)
        if card.main_benefit:
            reason = card.main_benefit
        # 2순위: benefits_summary 필드
        elif card.benefits_summary:
            reason = card.benefits_summary

        if reason:
            # 너무 길지 않게 자르고, "대표 혜택: " 접두사 추가
            reason_text = reason[:50]
            if len(reason) > 50:
                reason_text += "..."
            return [f"대표 혜택: {reason_text}"]

        # 최후의 보루: 아무 혜택 정보도 없을 경우
        return ["다양한 혜택 제공"]

    def recommend(
        self,
        query: str,
        k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[RecommendHit]:
        """
        하이브리드 카드 추천

        Args:
            query: 자연어 질의
            k: 반환할 카드 수
            filters: {
                'company': str,
                'card_type': 'CRD' | 'CHK',
                'max_annual_fee': int,
                'max_min_spending': int,
                'category_weights': {'COFFEE': 3, 'FOOD': 2, ...}
            }

        Returns:
            RecommendHit 리스트
        """
        filters = filters or {}
        category_weights = filters.get('category_weights', {})

        # 1. SQL 후보군 (순서 보장)
        sql_candidates = self._get_sql_candidates(filters)

        # 2. Chroma 후보군
        chroma_candidates = self._get_chroma_candidates(query, filters)

        # 3. 후보 합치기 (순서 보존)
        if chroma_candidates:
            final_gids = []
            seen_gids = set()
            sql_candidates_set = set(sql_candidates)

            # 1. 교집합: Chroma 결과 중 SQL 하드 필터를 통과한 카드들 (Chroma 순서 유지)
            for gid in chroma_candidates.keys():
                if gid in sql_candidates_set:
                    if gid not in seen_gids:
                        final_gids.append(gid)
                        seen_gids.add(gid)

            # 2. Fallback: 교집합만으로 후보가 부족할 경우, SQL 후보군에서 추가 (랭킹 순)
            if len(final_gids) < k * 3:
                for gid in sql_candidates:
                    if len(final_gids) >= k * 3:
                        break
                    if gid not in seen_gids:
                        final_gids.append(gid)
                        seen_gids.add(gid)
        else:
            # Chroma 검색이 없으면 그냥 SQL 결과 사용
            final_gids = sql_candidates

        if not final_gids:
            return []

        # 4. DB에서 카드 조회
        cards = Card.objects.filter(gorilla_id__in=final_gids)
        card_map = {c.gorilla_id: c for c in cards}

        # 5. 점수 계산
        scored: List[tuple] = []

        for gid in final_gids:
            card = card_map.get(gid)
            if not card:
                continue

            # semantic score
            chroma_data = chroma_candidates.get(gid, {})
            semantic_score = chroma_data.get('score', 0.0)

            # fit score
            fit_score = self._calc_fit_score(card, category_weights)

            # total score (Semantic + Fit)
            total = (
                self.WEIGHT_SEMANTIC * semantic_score +
                self.WEIGHT_FIT * fit_score
            )

            # 랭킹 보너스 (작은 보정)
            if card.ranking:
                ranking_bonus = max(0, (100 - card.ranking) / 1000.0)
                total += ranking_bonus

            preview = chroma_data.get('preview', '')
            if not preview and card.benefits_summary:
                preview = card.benefits_summary[:100]
                if len(preview) > 80:
                    preview = preview[:80] + "..."

            reasons = self._generate_reasons(card, semantic_score, fit_score, category_weights)

            # 이유가 비어있으면 preview 텍스트를 기반으로 생성
            if not reasons and preview:
                # "주요 혜택: " 같은 접두사를 붙여 일관성 유지
                reason_text = preview.replace('...', '')
                if "대표 혜택" not in reason_text and "혜택" not in reason_text:
                    reason_text = f"주요 혜택: {reason_text}"
                reasons.append(reason_text)

            scored.append(
                (
                    total,
                    RecommendHit(
                        gorilla_id=gid,
                        score=total,
                        semantic_score=semantic_score,
                        fit_score=fit_score,
                        preview=preview,
                        reasons=reasons,
                        name=card.name,
                        company=card.company,
                        ranking=card.ranking,
                    ),
                )
            )

        # 6. 정렬 및 반환
        scored.sort(key=lambda x: x[0], reverse=True)
        return [hit for _, hit in scored[:k]]

    def recommend_simple(self, query: str, k: int = 5) -> List[RecommendHit]:
        """기존 호환용 단순 추천 (필터 없음)"""
        return self.recommend(query, k=k, filters={})

    def recommend_by_profile(
        self,
        filters: Dict[str, Any],
        k: int = 10
    ) -> List[RecommendHit]:
        """
        선호도만으로 카드 추천 (query 없이 category_weights 기반)

        Args:
            filters: {
                'category_weights': {'COFFEE': 3, 'FOOD': 2, ...},
                'max_annual_fee': int,
                'max_min_spending': int,
            }
            k: 반환할 카드 수

        Returns:
            RecommendHit 리스트 (fit_score 기반 정렬)
        """
        category_weights = filters.get('category_weights', {})

        if not category_weights:
            return []

        # SQL 후보군 조회
        sql_candidates = self._get_sql_candidates(filters)

        if not sql_candidates:
            return []

        # DB에서 카드 조회
        cards = Card.objects.filter(gorilla_id__in=sql_candidates)
        card_map = {c.gorilla_id: c for c in cards}

        # 점수 계산 (fit_score 중심)
        category_map = dict(Card.CATEGORY_CHOICES)
        scored: List[tuple] = []

        for gid in sql_candidates:
            card = card_map.get(gid)
            if not card:
                continue

            # fit score (선호도 매칭)
            fit_score = self._calc_fit_score(card, category_weights)

            # 선호도가 0인 카드는 제외
            if fit_score == 0:
                continue

            # total score (Fit only, Semantic 없음)
            total = fit_score

            # 랭킹 보너스
            if card.ranking:
                ranking_bonus = max(0, (100 - card.ranking) / 1000.0)
                total += ranking_bonus

            # preview 생성
            preview = ""
            if card.benefits_summary:
                preview = card.benefits_summary[:80]
                if len(card.benefits_summary) > 80:
                    preview += "..."

            # 추천 이유 생성 (선호 카테고리 기반)
            matched_cats = [cat for cat in card.categories if category_weights.get(cat, 0) > 0]
            if matched_cats:
                cat_names = [category_map.get(c, c) for c in matched_cats[:3]]
                reasons = [f"선호 카테고리: {', '.join(cat_names)}"]
            else:
                reasons = self._generate_reasons(card)

            scored.append(
                (
                    total,
                    RecommendHit(
                        gorilla_id=gid,
                        score=total,
                        semantic_score=0.0,
                        fit_score=fit_score,
                        preview=preview,
                        reasons=reasons,
                        name=card.name,
                        company=card.company,
                        ranking=card.ranking,
                    ),
                )
            )

        # 정렬 및 반환
        scored.sort(key=lambda x: x[0], reverse=True)
        return [hit for _, hit in scored[:k]]

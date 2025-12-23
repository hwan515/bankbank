from django.db import models
from django.conf import settings
import hashlib
import re


class Card(models.Model):
    """신용카드 기본 정보"""
    CARD_TYPE_CHOICES = [
        ('CRD', '신용카드'),
        ('CHK', '체크카드'),
    ]

    CATEGORY_CHOICES = [
        ('TRANS', '교통'),
        ('COMM', '통신'),
        ('SHOP', '쇼핑'),
        ('COFFEE', '카페'),
        ('FOOD', '음식'),
        ('GAS', '주유'),
        ('UTIL', '공과금'),
        ('SUB', '구독'),
        ('PAY', '간편결제'),
        ('TRAVEL', '여행'),
        ('MART', '마트'),
        ('CULTURE', '문화'),
        ('MEDICAL', '의료'),
        ('EDU', '교육'),
        ('ETC', '기타'),
    ]

    gorilla_id = models.IntegerField(unique=True, help_text="카드고릴라 고유 ID")
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=100)
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, default='CRD')
    annual_fee = models.CharField(max_length=200, blank=True, help_text="연회비 정보")
    annual_fee_min = models.IntegerField(default=0, help_text="최소 연회비(원) - 필터용")
    min_spending = models.IntegerField(default=0, help_text="전월실적 조건(원)")

    benefits_summary = models.TextField(blank=True, help_text="혜택 요약 텍스트")
    benefits_json = models.JSONField(default=list, help_text="원본 혜택 JSON")
    structured_benefit = models.JSONField(default=list, help_text="정규화된 혜택 JSON")

    categories = models.JSONField(default=list, help_text="모든 혜택 카테고리 목록")

    ranking = models.IntegerField(null=True, blank=True, help_text="인기 순위")
    crawled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['ranking', '-created_at']
        indexes = [
            models.Index(fields=['ranking']),
            models.Index(fields=['company']),
            models.Index(fields=['card_type']),
            models.Index(fields=['min_spending']),
            models.Index(fields=['annual_fee_min']),
        ]

    def __str__(self):
        return f"{self.company} - {self.name}"

    @property
    def image_url(self) -> str:
        """gorilla_id 기반 이미지 URL 생성"""
        return f'https://cardimage.cocohwan.site/{self.gorilla_id}.png'

    @property
    def main_benefit(self) -> str:
        """대표 혜택 텍스트 반환"""
        if self.benefits_json and isinstance(self.benefits_json, list):
            first = self.benefits_json[0] if self.benefits_json else {}
            return first.get('title', '') or first.get('summary', '')
        return self.benefits_summary[:50] if self.benefits_summary else ''

    @property
    def primary_category(self) -> str:
        """첫 번째 카테고리 코드 반환 (동적 계산)"""
        if self.categories:
            return self.categories[0]
        return 'ETC'

    @property
    def category(self) -> str:
        """대표 카테고리 한글명 반환"""
        category_map = dict(self.CATEGORY_CHOICES)
        return category_map.get(self.primary_category, '기타')

    @property
    def category_names(self) -> list:
        """모든 카테고리 한글명 목록"""
        category_map = dict(self.CATEGORY_CHOICES)
        return [category_map.get(cat, cat) for cat in self.categories]

    def get_benefits_by_category(self) -> dict:
        """카테고리별 혜택 그룹화"""
        if not self.structured_benefit:
            return {}
        result = {}
        for b in self.structured_benefit:
            cat = b.get('category', 'ETC')
            if cat not in result:
                result[cat] = []
            result[cat].append(b)
        return result

    def get_top_benefit_per_category(self) -> dict:
        """카테고리별 최고 혜택 반환 (value 기준)"""
        by_cat = self.get_benefits_by_category()
        result = {}
        for cat, benefits in by_cat.items():
            # value가 가장 큰 혜택 선택
            best = max(benefits, key=lambda x: float(x.get('value', 0) or 0))
            result[cat] = best
        return result

    def parse_annual_fee(self) -> int:
        """연회비 문자열에서 최소 연회비(숫자) 추출"""
        if not self.annual_fee:
            return 0
        numbers = re.findall(r'[\d,]+', self.annual_fee.replace(',', ''))
        if numbers:
            try:
                return min(int(n.replace(',', '')) for n in numbers if n.replace(',', '').isdigit())
            except (ValueError, TypeError):
                return 0
        return 0

    # 한글 카테고리 → 영문 코드 매핑
    CATEGORY_KO_TO_CODE = {
        '교통': 'TRANS', '대중교통': 'TRANS',
        '통신': 'COMM', '휴대폰': 'COMM',
        '쇼핑': 'SHOP', '온라인쇼핑': 'SHOP', '백화점': 'SHOP',
        '카페': 'COFFEE', '커피': 'COFFEE', '스타벅스': 'COFFEE',
        '음식': 'FOOD', '외식': 'FOOD', '식당': 'FOOD', '배달': 'FOOD',
        '주유': 'GAS', '주유소': 'GAS',
        '공과금': 'UTIL', '관리비': 'UTIL', '세금': 'UTIL',
        '구독': 'SUB', 'OTT': 'SUB', '스트리밍': 'SUB',
        '간편결제': 'PAY', '페이': 'PAY',
        '여행': 'TRAVEL', '항공': 'TRAVEL', '호텔': 'TRAVEL', '해외': 'TRAVEL',
        '마트': 'MART', '편의점': 'MART', '대형마트': 'MART',
        '문화': 'CULTURE', '영화': 'CULTURE', '공연': 'CULTURE', '전시': 'CULTURE', '도서': 'CULTURE',
        '의료': 'MEDICAL', '병원': 'MEDICAL', '약국': 'MEDICAL', '한의원': 'MEDICAL',
        '교육': 'EDU', '학원': 'EDU', '학습지': 'EDU', '유치원': 'EDU',
        '기타': 'ETC', '보험': 'ETC',
    }

    def extract_categories(self) -> list:
        """structured_benefit에서 카테고리 목록 추출 (한글→영문 코드 변환)"""
        if not self.structured_benefit:
            return []

        valid_codes = {code for code, _ in self.CATEGORY_CHOICES}
        seen = set()
        cats = []

        for b in self.structured_benefit:
            cat = b.get('category', '')
            if not cat:
                continue

            # 이미 영문 코드인 경우
            if cat in valid_codes:
                code = cat
            # 한글인 경우 변환
            elif cat in self.CATEGORY_KO_TO_CODE:
                code = self.CATEGORY_KO_TO_CODE[cat]
            else:
                code = 'ETC'

            if code not in seen:
                seen.add(code)
                cats.append(code)

        return cats

    def sync_computed_fields(self) -> bool:
        """연회비, 카테고리 등 계산 필드 동기화. 변경 여부 반환"""
        changed = False

        new_fee = self.parse_annual_fee()
        if self.annual_fee_min != new_fee:
            self.annual_fee_min = new_fee
            changed = True

        new_cats = self.extract_categories()
        if self.categories != new_cats:
            self.categories = new_cats
            changed = True

        return changed

    def build_embedding_text(self) -> str:
        """Chroma에 넣을 임베딩용 텍스트 생성"""
        parts = [
            f"카드명: {self.name}",
            f"발급사: {self.company}",
            f"카드종류: {self.get_card_type_display()}",
        ]
        if self.annual_fee:
            parts.append(f"연회비: {self.annual_fee}")
        if self.min_spending:
            parts.append(f"전월실적: {self.min_spending:,}원")
        if self.benefits_summary:
            parts.append(f"혜택요약: {self.benefits_summary}")

        if self.structured_benefit:
            lines = []
            category_map = dict(self.CATEGORY_CHOICES)
            for b in self.structured_benefit[:10]:
                cat = b.get('category', 'ETC')
                cat_name = category_map.get(cat, '기타')
                title = b.get('title') or b.get('name') or ''
                desc = b.get('desc') or b.get('summary') or ''
                if title or desc:
                    lines.append(f"[{cat_name}] {title} {desc}".strip())
            if lines:
                parts.append("혜택상세: " + " / ".join(lines))

        return "\n".join(parts)


class UserProfile(models.Model):
    """사용자 추천 프로필 (설문/선호도)"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='card_profile'
    )
    monthly_spend = models.IntegerField(default=0, help_text="월 평균 소비 금액(원)")
    category_weights = models.JSONField(
        default=dict, help_text="카테고리별 선호 가중치 {'COFFEE': 3, 'FOOD': 2, ...}"
    )
    fee_tolerance = models.IntegerField(default=0, help_text="연회비 허용 상한(원)")
    min_spend_tolerance = models.IntegerField(default=0, help_text="전월실적 허용 상한(원)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"Profile: {self.user.username}"


class UserEvent(models.Model):
    """사용자 행동 로그 (클릭/좋아요/신청)"""
    EVENT_CHOICES = [
        ('VIEW', '조회'),
        ('CLICK', '클릭'),
        ('LIKE', '좋아요'),
        ('APPLY', '신청'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='card_events', null=True, blank=True
    )
    card = models.ForeignKey('Card', on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=10, choices=EVENT_CHOICES)
    context = models.JSONField(default=dict, help_text="추가 컨텍스트 (화면, 쿼리 등)")
    session_id = models.CharField(max_length=100, blank=True, help_text="비로그인 사용자 세션")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['card', 'created_at']),
            models.Index(fields=['event_type', 'created_at']),
        ]


class RecommendationLog(models.Model):
    """추천 요청/결과 로그"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='recommendation_logs'
    )
    session_id = models.CharField(max_length=100, blank=True)
    query_text = models.TextField(blank=True, help_text="자연어 질의")
    filters = models.JSONField(default=dict, help_text="적용된 필터")

    result_card_ids = models.JSONField(default=list, help_text="추천 결과 카드 ID 목록")
    result_scores = models.JSONField(default=list, help_text="추천 점수 목록")

    processing_time_ms = models.IntegerField(default=0, help_text="처리 시간(ms)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['created_at']),
        ]


class CardEmbeddingState(models.Model):
    """카드 임베딩 동기화 상태"""
    card = models.OneToOneField('Card', on_delete=models.CASCADE, related_name='embedding_state')
    doc_id = models.CharField(max_length=100, unique=True, help_text="Chroma document ID")

    embedding_version = models.IntegerField(default=1)
    content_hash = models.CharField(max_length=64, blank=True, help_text="임베딩 텍스트 해시")
    needs_embedding = models.BooleanField(default=True, db_index=True)

    last_indexed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['needs_embedding']),
            models.Index(fields=['embedding_version']),
        ]

    @staticmethod
    def make_hash(text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def check_needs_update(self, card: 'Card') -> bool:
        """카드 내용이 변경되어 재임베딩이 필요한지 확인"""
        new_text = card.build_embedding_text()
        new_hash = self.make_hash(new_text)
        return self.content_hash != new_hash

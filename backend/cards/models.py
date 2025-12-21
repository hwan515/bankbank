from django.db import models


class Card(models.Model):
    """신용카드 기본 정보"""
    CARD_TYPE_CHOICES = [
        ('credit', '신용카드'),
        ('check', '체크카드'),
    ]

    gorilla_id = models.IntegerField(unique=True, help_text="카드고릴라 고유 ID")
    name = models.CharField(max_length=200)
    company = models.CharField(max_length=100)
    card_type = models.CharField(max_length=20, choices=CARD_TYPE_CHOICES, default='credit')
    annual_fee = models.CharField(max_length=200, blank=True, help_text="연회비 정보")
    min_spending = models.IntegerField(default=0, help_text="전월실적 조건(원)")

    benefits_summary = models.TextField(blank=True, help_text="혜택 요약 텍스트")
    benefits_json = models.JSONField(default=list, help_text="원본 혜택 JSON")
    structured_benefit = models.JSONField(default=list, help_text="정규화된 혜택 JSON")

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
    def category(self) -> str:
        """structured_benefit 기반 대표 카테고리"""
        if not self.structured_benefit:
            return '기타'
        category_map = {
            'TRANS': '교통', 'COMM': '통신', 'SHOP': '쇼핑',
            'COFFEE': '카페', 'FOOD': '외식', 'GAS': '주유',
            'UTIL': '공과금', 'SUB': '구독', 'PAY': '페이', 'ETC': '기타'
        }
        first_cat = self.structured_benefit[0].get('category', 'ETC') if self.structured_benefit else 'ETC'
        return category_map.get(first_cat, '기타')

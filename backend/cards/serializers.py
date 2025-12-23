from rest_framework import serializers
from .models import Card, UserProfile, UserEvent, RecommendationLog


class CardListSerializer(serializers.ModelSerializer):
    """카드 목록용 (간략 정보)"""
    main_benefit = serializers.CharField(read_only=True)
    category = serializers.CharField(read_only=True)
    category_names = serializers.ListField(read_only=True)
    primary_category = serializers.CharField(read_only=True)
    image_url = serializers.CharField(read_only=True)

    class Meta:
        model = Card
        fields = [
            'id', 'gorilla_id', 'name', 'company', 'card_type',
            'annual_fee', 'annual_fee_min', 'min_spending',
            'ranking', 'main_benefit', 'category', 'categories',
            'category_names', 'primary_category', 'image_url'
        ]


class CardDetailSerializer(serializers.ModelSerializer):
    """카드 상세 정보"""
    main_benefit = serializers.CharField(read_only=True)
    category = serializers.CharField(read_only=True)
    category_names = serializers.ListField(read_only=True)
    primary_category = serializers.CharField(read_only=True)
    benefits_by_category = serializers.SerializerMethodField()
    image_url = serializers.CharField(read_only=True)

    class Meta:
        model = Card
        fields = [
            'id', 'gorilla_id', 'name', 'company', 'card_type',
            'annual_fee', 'annual_fee_min', 'min_spending', 'ranking',
            'benefits_summary', 'benefits_json', 'structured_benefit',
            'main_benefit', 'category', 'categories', 'category_names',
            'primary_category', 'benefits_by_category',
            'image_url', 'created_at', 'updated_at'
        ]

    def get_benefits_by_category(self, obj):
        """카테고리별 최고 혜택"""
        return obj.get_top_benefit_per_category()


class CardRecommendRequestSerializer(serializers.Serializer):
    """AI 추천 요청 (필터 포함)"""
    query = serializers.CharField(max_length=500, help_text="자연어 질의")
    k = serializers.IntegerField(default=5, min_value=1, max_value=50)

    # 하드 필터 (절대 조건)
    company = serializers.CharField(required=False, allow_blank=True, help_text="카드사 필터")
    card_type = serializers.ChoiceField(
        required=False, choices=[('CRD', '신용'), ('CHK', '체크')],
        help_text="카드 종류"
    )
    max_annual_fee = serializers.IntegerField(
        required=False, min_value=0, help_text="연회비 상한(원)"
    )
    max_min_spending = serializers.IntegerField(
        required=False, min_value=0, help_text="전월실적 상한(원)"
    )

    # 소프트 필터 (선호도)
    preferred_categories = serializers.ListField(
        child=serializers.CharField(max_length=10),
        required=False, default=list,
        help_text="선호 카테고리 목록 ['COFFEE', 'FOOD', ...]"
    )
    category_weights = serializers.DictField(
        child=serializers.FloatField(min_value=0, max_value=10),
        required=False, default=dict,
        help_text="카테고리별 가중치 {'COFFEE': 3, 'FOOD': 2}"
    )

    def validate_company(self, v):
        return v.strip() if v else ''


class CardRecommendResultSerializer(serializers.Serializer):
    """AI 추천 결과"""
    card = CardListSerializer()
    score = serializers.FloatField()
    semantic_score = serializers.FloatField()
    fit_score = serializers.FloatField()
    reasons = serializers.ListField(child=serializers.CharField())
    preview = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    """사용자 추천 프로필"""
    class Meta:
        model = UserProfile
        fields = [
            'monthly_spend', 'category_weights',
            'fee_tolerance', 'min_spend_tolerance',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class UserEventSerializer(serializers.ModelSerializer):
    """사용자 행동 로그"""
    class Meta:
        model = UserEvent
        fields = ['card', 'event_type', 'context', 'created_at']
        read_only_fields = ['created_at']


class UserEventCreateSerializer(serializers.Serializer):
    """이벤트 생성용"""
    card_id = serializers.IntegerField()
    event_type = serializers.ChoiceField(choices=['VIEW', 'CLICK', 'LIKE', 'APPLY'])
    context = serializers.DictField(required=False, default=dict)

from rest_framework import serializers
from .models import Card


class CardListSerializer(serializers.ModelSerializer):
    """카드 목록용 (간략 정보)"""
    main_benefit = serializers.CharField(read_only=True)
    category = serializers.CharField(read_only=True)
    image_url = serializers.CharField(read_only=True)

    class Meta:
        model = Card
        fields = [
            'id', 'gorilla_id', 'name', 'company', 'card_type',
            'annual_fee', 'ranking', 'main_benefit', 'category', 'image_url'
        ]


class CardDetailSerializer(serializers.ModelSerializer):
    """카드 상세 정보"""
    main_benefit = serializers.CharField(read_only=True)
    category = serializers.CharField(read_only=True)
    image_url = serializers.CharField(read_only=True)

    class Meta:
        model = Card
        fields = [
            'id', 'gorilla_id', 'name', 'company', 'card_type',
            'annual_fee', 'min_spending', 'ranking',
            'benefits_summary', 'benefits_json', 'structured_benefit',
            'main_benefit', 'category', 'image_url',
            'created_at', 'updated_at'
        ]


class CardRecommendRequestSerializer(serializers.Serializer):
    """AI 추천 요청"""
    query = serializers.CharField(max_length=500, help_text="자연어 질의")
    k = serializers.IntegerField(default=5, min_value=1, max_value=20)


class CardRecommendResultSerializer(serializers.Serializer):
    """AI 추천 결과"""
    card = CardListSerializer()
    score = serializers.FloatField()
    preview = serializers.CharField()

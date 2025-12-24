from rest_framework import serializers
from .models import (
    DepositProducts,
    DepositOptions,
    SavingProducts,
    SavingOptions,
    DepositSubscription,
    SavingSubscription,
)


def _best_rate_and_term(obj):
    rates = {
        6: obj.intr_rate_6,
        12: obj.intr_rate_12,
        24: obj.intr_rate_24,
        36: obj.intr_rate_36,
    }
    available = {term: rate for term, rate in rates.items() if rate is not None}
    if not available:
        return None, None

    best_rate = max(available.values())
    best_terms = [term for term, rate in available.items() if rate == best_rate]
    return best_rate, min(best_terms)


class DepositOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositOptions
        fields = '__all__'
        read_only_fields = ('product',)


class DepositProductsSerializer(serializers.ModelSerializer):
    options = DepositOptionsSerializer(many=True, read_only=True)

    class Meta:
        model = DepositProducts
        fields = '__all__'


class DepositProductsListSerializer(serializers.ModelSerializer):
    """목록 조회용 - 기간별 금리 포함 (최적화)"""
    intr_rate_6 = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    intr_rate_12 = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    intr_rate_24 = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    intr_rate_36 = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    best_rate = serializers.SerializerMethodField()
    best_term = serializers.SerializerMethodField()

    class Meta:
        model = DepositProducts
        fields = ['id', 'dcls_month', 'fin_prdt_cd', 'kor_co_nm', 'fin_prdt_nm',
                  'intr_rate_6', 'intr_rate_12', 'intr_rate_24', 'intr_rate_36',
                  'best_rate', 'best_term']

    def get_best_rate(self, obj):
        best_rate, _ = _best_rate_and_term(obj)
        return best_rate

    def get_best_term(self, obj):
        _, best_term = _best_rate_and_term(obj)
        return best_term


class SavingOptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingOptions
        fields = '__all__'
        read_only_fields = ('product',)


class SavingProductsSerializer(serializers.ModelSerializer):
    saving_options = SavingOptionsSerializer(many=True, read_only=True)

    class Meta:
        model = SavingProducts
        fields = '__all__'


class SavingProductsListSerializer(serializers.ModelSerializer):
    """목록 조회용 - 기간별 금리 포함 (최적화)"""
    intr_rate_6 = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    intr_rate_12 = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    intr_rate_24 = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    intr_rate_36 = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    best_rate = serializers.SerializerMethodField()
    best_term = serializers.SerializerMethodField()

    class Meta:
        model = SavingProducts
        fields = ['id', 'dcls_month', 'fin_prdt_cd', 'kor_co_nm', 'fin_prdt_nm',
                  'intr_rate_6', 'intr_rate_12', 'intr_rate_24', 'intr_rate_36',
                  'best_rate', 'best_term']

    def get_best_rate(self, obj):
        best_rate, _ = _best_rate_and_term(obj)
        return best_rate

    def get_best_term(self, obj):
        _, best_term = _best_rate_and_term(obj)
        return best_term


class SimpleDepositProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositProducts
        fields = ['id', 'fin_prdt_nm', 'kor_co_nm']


class SimpleSavingProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingProducts
        fields = ['id', 'fin_prdt_nm', 'kor_co_nm']


class DepositSubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='product.id', read_only=True)
    fin_prdt_nm = serializers.CharField(source='product.fin_prdt_nm', read_only=True)
    kor_co_nm = serializers.CharField(source='product.kor_co_nm', read_only=True)
    subscription_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = DepositSubscription
        fields = [
            'id',
            'subscription_id',
            'fin_prdt_nm',
            'kor_co_nm',
            'term_months',
            'created_at',
            'updated_at',
        ]


class SavingSubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='product.id', read_only=True)
    fin_prdt_nm = serializers.CharField(source='product.fin_prdt_nm', read_only=True)
    kor_co_nm = serializers.CharField(source='product.kor_co_nm', read_only=True)
    subscription_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = SavingSubscription
        fields = [
            'id',
            'subscription_id',
            'fin_prdt_nm',
            'kor_co_nm',
            'term_months',
            'rsrv_type',
            'monthly_amount',
            'created_at',
            'updated_at',
        ]

from rest_framework import serializers
from .models import DepositProducts, DepositOptions, SavingProducts, SavingOptions


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

    class Meta:
        model = DepositProducts
        fields = ['id', 'dcls_month', 'fin_prdt_cd', 'kor_co_nm', 'fin_prdt_nm',
                  'intr_rate_6', 'intr_rate_12', 'intr_rate_24', 'intr_rate_36']


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

    class Meta:
        model = SavingProducts
        fields = ['id', 'dcls_month', 'fin_prdt_cd', 'kor_co_nm', 'fin_prdt_nm',
                  'intr_rate_6', 'intr_rate_12', 'intr_rate_24', 'intr_rate_36']

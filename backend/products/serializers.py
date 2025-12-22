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
    """목록 조회용 - 기간별 금리 포함"""
    intr_rate_6 = serializers.SerializerMethodField()
    intr_rate_12 = serializers.SerializerMethodField()
    intr_rate_24 = serializers.SerializerMethodField()
    intr_rate_36 = serializers.SerializerMethodField()

    class Meta:
        model = DepositProducts
        fields = ['id', 'dcls_month', 'fin_prdt_cd', 'kor_co_nm', 'fin_prdt_nm',
                  'intr_rate_6', 'intr_rate_12', 'intr_rate_24', 'intr_rate_36']

    def _get_rate_by_term(self, obj, term):
        """특정 기간의 금리 반환 (최고 우대금리 우선)"""
        option = obj.options.filter(save_trm=term).first()
        if option:
            return option.intr_rate2 or option.intr_rate
        return None

    def get_intr_rate_6(self, obj):
        return self._get_rate_by_term(obj, 6)

    def get_intr_rate_12(self, obj):
        return self._get_rate_by_term(obj, 12)

    def get_intr_rate_24(self, obj):
        return self._get_rate_by_term(obj, 24)

    def get_intr_rate_36(self, obj):
        return self._get_rate_by_term(obj, 36)


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
    """목록 조회용 - 기간별 금리 포함"""
    intr_rate_6 = serializers.SerializerMethodField()
    intr_rate_12 = serializers.SerializerMethodField()
    intr_rate_24 = serializers.SerializerMethodField()
    intr_rate_36 = serializers.SerializerMethodField()

    class Meta:
        model = SavingProducts
        fields = ['id', 'dcls_month', 'fin_prdt_cd', 'kor_co_nm', 'fin_prdt_nm',
                  'intr_rate_6', 'intr_rate_12', 'intr_rate_24', 'intr_rate_36']

    def _get_rate_by_term(self, obj, term):
        """특정 기간의 금리 반환 (최고 우대금리 우선)"""
        option = obj.saving_options.filter(save_trm=term).first()
        if option:
            return option.intr_rate2 or option.intr_rate
        return None

    def get_intr_rate_6(self, obj):
        return self._get_rate_by_term(obj, 6)

    def get_intr_rate_12(self, obj):
        return self._get_rate_by_term(obj, 12)

    def get_intr_rate_24(self, obj):
        return self._get_rate_by_term(obj, 24)

    def get_intr_rate_36(self, obj):
        return self._get_rate_by_term(obj, 36)

from django.contrib import admin
from .models import DepositProducts, DepositOptions, SavingProducts, SavingOptions

# Register your models here.
@admin.register(DepositProducts)
class DepositProductsAdmin(admin.ModelAdmin):
    list_display = ('fin_prdt_cd', 'kor_co_nm', 'fin_prdt_nm')
    search_fields = ('fin_prdt_nm', 'kor_co_nm')

@admin.register(DepositOptions)
class DepositOptionsAdmin(admin.ModelAdmin):
    list_display = ('product', 'save_trm', 'intr_rate', 'intr_rate2')

@admin.register(SavingProducts)
class SavingProductsAdmin(admin.ModelAdmin):
    list_display = ('fin_prdt_cd', 'kor_co_nm', 'fin_prdt_nm')

@admin.register(SavingOptions)
class SavingOptionsAdmin(admin.ModelAdmin):
    list_display = ('product', 'save_trm', 'rsrv_type_nm', 'intr_rate')
from django.urls import path
from . import views

urlpatterns = [
    # 데이터 저장
    path('save-financial-companies/', views.save_financial_companies, name='save_financial_companies'),
    path('save-deposit-products/', views.save_deposit_products, name='save_deposit_products'),
    path('save-saving-products/', views.save_saving_products, name='save_saving_products'),

    # 금융회사 목록
    path('financial-companies/', views.financial_companies, name='financial_companies'),

    # 목록 조회 (필터/검색/정렬 지원)
    path('deposit-products/', views.deposit_products, name='deposit_products'),
    path('saving-products/', views.saving_products, name='saving_products'),

    # 상세 조회
    path('deposit-products/<int:pk>/', views.deposit_product_detail, name='deposit_product_detail'),
    path('saving-products/<int:pk>/', views.saving_product_detail, name='saving_product_detail'),

    # [F03-3] 상품 가입/해제
    path('deposit-products/<int:pk>/subscribe/', views.subscribe_deposit, name='subscribe_deposit'),
    path('saving-products/<int:pk>/subscribe/', views.subscribe_saving, name='subscribe_saving'),

    # [F03-3] 가입 여부 확인
    path('check-subscription/<str:product_type>/<int:pk>/', views.check_subscription, name='check_subscription'),

    # 은행 목록 - 추후 지도 개발 때 사용
    path('banks/', views.bank_list, name='bank_list'),
]
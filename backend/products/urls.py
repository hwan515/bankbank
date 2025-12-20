from django.urls import path
from . import views

urlpatterns = [
    path('save-deposit-products/', views.save_deposit_products, name='save_deposit_products'),
    path('save-saving-products/', views.save_saving_products, name='save_saving_products'),
    path('deposit-products/', views.deposit_products, name='deposit_products'),
    path('saving-products/', views.saving_products, name='saving_products'),
]
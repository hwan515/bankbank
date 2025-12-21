from django.urls import path
from . import views

urlpatterns = [
    path('', views.card_list, name='card-list'),
    path('companies/', views.card_companies, name='card-companies'),
    path('card-recommendation/', views.card_recommend, name='card-recommendation'),
    path('<int:pk>/', views.card_detail, name='card-detail'),
]

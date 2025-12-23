from django.urls import path
from . import views

urlpatterns = [
    # 카드 목록/상세
    path('', views.card_list, name='card-list'),
    path('companies/', views.card_companies, name='card-companies'),
    path('categories/', views.card_categories, name='card-categories'),
    path('<int:pk>/', views.card_detail, name='card-detail'),

    # AI 추천
    path('card-recommendation/', views.card_recommend, name='card-recommendation'),

    # 사용자 행동 로그
    path('events/', views.card_event, name='card-event'),

    # 사용자 프로필 (추천용)
    path('profile/', views.user_profile, name='card-profile'),
]

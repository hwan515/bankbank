from django.urls import path
from . import views

urlpatterns = [
    # 카드 목록/상세
    path('', views.card_list, name='card-list'),
    path('companies/', views.card_companies, name='card-companies'),
    path('categories/', views.card_categories, name='card-categories'),

    # AI 추천
    path('card-recommendation/', views.card_recommend, name='card-recommendation'),

    # 사용자 행동 로그
    path('events/', views.card_event, name='card-event'),

    # 사용자 프로필 (추천용)
    path('profile/', views.user_profile, name='card-profile'),

    # 마이페이지 - 좋아요/최근본/추천이력
    path('my/liked/', views.my_liked_cards, name='my-liked-cards'),
    path('my/recent/', views.my_recent_cards, name='my-recent-cards'),
    path('my/recommendations/', views.my_recommendation_history, name='my-recommendations'),

    # 카드 상세/좋아요 (pk 기반 - 맨 아래 배치)
    path('<int:pk>/', views.card_detail, name='card-detail'),
    path('<int:pk>/like/', views.toggle_like, name='card-like'),
]

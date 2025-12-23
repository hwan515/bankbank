from django.urls import path
from recommend.views import RecommendCardsView

urlpatterns = [
    path("cards/", RecommendCardsView.as_view()),
]

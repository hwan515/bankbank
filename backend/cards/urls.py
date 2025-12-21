from django.urls import path
from . import views

urlpatterns = [
    path('card-recommendation/', views.card_recommend, name='card-recommendation'),
]

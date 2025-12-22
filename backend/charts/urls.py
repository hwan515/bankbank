from django.urls import path
from . import views

urlpatterns = [
    path("gold/", views.gold_chart),
]

from django.urls import path
from . import views

urlpatterns = [
    path("chart/", views.metal_chart),
]

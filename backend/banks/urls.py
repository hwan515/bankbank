from django.urls import path
from .views import directions

urlpatterns = [
    path("directions/", directions),
]

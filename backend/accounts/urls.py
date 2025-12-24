
from django.contrib import admin
from django.urls import path, include
from .views import load_profile, information, user_search
urlpatterns = [
    path('profile/', load_profile),
    path('information/', information),
    path("users/search/", user_search),

]

from django.urls import path
from . import views

urlpatterns = [
    path("rooms/", views.room_list),
    path("rooms/create/", views.room_create),
    path("rooms/<int:room_id>/join/", views.room_join),
    path("rooms/<int:room_id>/messages/", views.message_list),
    path("lobby/ensure/", views.ensure_lobby),
    path("dm/ensure/", views.ensure_dm_by_username),
    path("dm/ensure/<int:other_user_id>/", views.ensure_dm),
    path("rooms/public/", views.public_room_list),


]


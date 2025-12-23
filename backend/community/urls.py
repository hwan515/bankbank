from django.urls import path
from . import views


urlpatterns = [
    path("posts/", views.post_list_create, name="post_list_create"),
    path("posts/<int:pk>/", views.post_detail, name="post_detail"),
    path(
        "posts/<int:pk>/<str:reaction>/",
        views.toggle_post_reaction,
        name="post_reaction",
    ),
    path(
        "posts/<int:post_pk>/comments/",
        views.comment_list_create,
        name="comment_list_create",
    ),
    path("comments/<int:pk>/", views.comment_detail, name="comment_detail"),
    path(
        "comments/<int:pk>/<str:reaction>/",
        views.toggle_comment_reaction,
        name="comment_reaction",
    ),
]

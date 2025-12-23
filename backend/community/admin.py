from django.contrib import admin
from .models import Post, Comment


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "board_type", "author", "created_at")
    list_filter = ("board_type", "created_at")
    search_fields = ("title", "content", "author__username")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "post", "author", "created_at")
    search_fields = ("content", "author__username")
    list_filter = ("created_at",)

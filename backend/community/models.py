from django.conf import settings
from django.db import models


class Post(models.Model):
    BOARD_CHOICES = [
        ("product", "금융상품 리뷰"),
        ("card", "카드 리뷰"),
    ]

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )
    board_type = models.CharField(max_length=20, choices=BOARD_CHOICES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_posts",
        blank=True,
    )
    dislike_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="disliked_posts",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField()
    like_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="liked_comments",
        blank=True,
    )
    dislike_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="disliked_comments",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author} - {self.content[:20]}"

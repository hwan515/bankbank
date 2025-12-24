from django.db import models
from django.conf import settings

class ChatRoom(models.Model):
    name = models.CharField(max_length=100, blank=True)
    is_lobby = models.BooleanField(default=False)
    is_dm = models.BooleanField(default=False)      # ✅ 추가
    dm_key = models.CharField(max_length=255, blank=True, db_index=True)  # ✅ 추가 (예: "3:10")
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="chat_rooms", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    # ✅ 최근 대화 기준
    last_message_at = models.DateTimeField(null=True, blank=True)


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name="messages")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="chat_messages")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

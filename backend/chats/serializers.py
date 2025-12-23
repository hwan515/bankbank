# chat/serializers.py
from rest_framework import serializers
from .models import ChatRoom, ChatMessage
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatRoomSerializer(serializers.ModelSerializer):
    dm_partner_username = serializers.SerializerMethodField()
    class Meta:
        model = ChatRoom
        fields = ["id", "name", "is_lobby", "is_public", "is_dm", "dm_key", 
                  "dm_partner_username", "last_message_at", # ✅ 추가
                  "created_at"]
        
    def get_dm_partner_username(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        if not obj.is_dm:
            return None

        me = request.user
        partner = obj.members.exclude(id=me.id).first()
        return partner.username if partner else None

class ChatMessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = ChatMessage
        fields = ["id", "room", "sender", "content", "created_at"]
        read_only_fields = ["id", "sender", "created_at"]

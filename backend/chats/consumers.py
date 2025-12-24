# chats/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from .models import ChatRoom, ChatMessage


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.room_id = int(self.scope["url_route"]["kwargs"]["room_id"])

        ok = await self._is_member(user.id, self.room_id)
        if not ok:
            await self.close(code=4003)
            return

        self.group_name = f"chat_{self.room_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        user = self.scope["user"]
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        content = (data.get("message") or "").strip()
        if not content:
            return

        # ✅ DB 작업은 sync_to_async로
        payload = await self._create_message_and_touch_room(
            room_id=self.room_id,
            user_id=user.id,
            content=content
        )

        # ✅ 브로드캐스트(모든 클라이언트로)
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",   # ✅ 언더스코어 권장
                **payload,
            },
        )

    async def chat_message(self, event):
        # event는 dict
        await self.send(text_data=json.dumps({
            "id": event["id"],
            "sender": event["sender"],
            "message": event["message"],
            "created_at": event["created_at"],
        }))

    @database_sync_to_async
    def _is_member(self, user_id, room_id):
        return ChatRoom.objects.filter(id=room_id, members__id=user_id).exists()

    @database_sync_to_async
    def _create_message_and_touch_room(self, room_id, user_id, content):
        room = ChatRoom.objects.get(id=room_id)

        # ✅ 너 모델 필드명이 sender라면 sender_id 사용
        msg = ChatMessage.objects.create(
            room=room,
            user_id=user_id,
            content=content,
        )

        # ✅ 최근 대화 시간 업데이트(정렬용)
        now = timezone.now()
        room.last_message_at = now
        room.save(update_fields=["last_message_at"])

        return {
            "id": msg.id,
            "sender": msg.user.username,
            "message": msg.content,
            "created_at": msg.created_at.isoformat(),
        }

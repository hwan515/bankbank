from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import ChatRoom
from .serializers import ChatRoomSerializer, ChatMessageSerializer

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def room_list(request):
    qs = ChatRoom.objects.filter(members=request.user).order_by("-last_message_at","-created_at")
    serializer = ChatRoomSerializer(qs, many=True, context={"request": request})
    return Response(serializer.data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def room_create(request):
    name = (request.data.get("name") or "").strip()
    room = ChatRoom.objects.create(name=name)
    room.members.add(request.user)
    return Response(ChatRoomSerializer(room).data, status=201)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def room_join(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    room.members.add(request.user)
    return Response(ChatRoomSerializer(room).data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def message_list(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, members=request.user)
    limit = int(request.GET.get("limit", 50))
    qs = room.messages.select_related("user").order_by("-created_at")[:limit]
    data = ChatMessageSerializer(reversed(qs), many=True).data
    return Response(data)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ChatRoom
from .serializers import ChatRoomSerializer

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ensure_lobby(request):
    lobby, _ = ChatRoom.objects.get_or_create(
        is_lobby=True,
        defaults={"name": "lobby", "is_public": True}
    )
    # 혹시 기존 로비가 public False로 생성된 적 있으면 보정
    if not lobby.is_public:
        lobby.is_public = True
        lobby.save(update_fields=["is_public"])

    lobby.members.add(request.user)
    return Response(ChatRoomSerializer(lobby).data)


from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import ChatRoom
from .serializers import ChatRoomSerializer

User = get_user_model()

def make_dm_key(a, b):
    x, y = sorted([a, b])
    return f"{x}:{y}"

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ensure_dm_by_username(request):
    username = (request.data.get("username") or "").strip()
    other = get_object_or_404(User, username=username)

    me = request.user
    if other.id == me.id:
        return Response({"detail": "자기 자신에게 DM은 안돼요."}, status=400)

    key = make_dm_key(me.id, other.id)

    room, _ = ChatRoom.objects.get_or_create(
        is_dm=True,
        dm_key=key,
        defaults={"name": f"dm-{key}"}
    )
    room.members.add(me, other)
    return Response(ChatRoomSerializer(room).data, status=200)


from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from .models import ChatRoom
from .serializers import ChatRoomSerializer

User = get_user_model()

def make_dm_key(a, b):
    x, y = sorted([a, b])
    return f"{x}:{y}"

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ensure_dm(request, other_user_id):
    other = get_object_or_404(User, id=other_user_id)

    me = request.user
    key = make_dm_key(me.id, other.id)

    room, created = ChatRoom.objects.get_or_create(
        is_dm=True,
        dm_key=key,
        defaults={"name": f"dm-{key}"}
    )
    room.members.add(me, other)

    return Response(ChatRoomSerializer(room, context={"request": request}).data)




@api_view(["GET"])
@permission_classes([IsAuthenticated])
def public_room_list(request):
    qs = ChatRoom.objects.filter(is_public=True).order_by("-created_at")
    serializer = ChatRoomSerializer(qs, many=True, context={"request": request})
    return Response(serializer.data)

from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, InformationSerializer
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User, Information
from rest_framework import status
# Create your views here.

@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])  # 필요에 따라 IsAuthenticated로 바꿔
def load_profile(request):
    user = request.user  
    if request.method == 'GET':
                  # 🔥 토큰으로 자동 식별된 사용자
        serializer = UserSerializer(user)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        serializer = UserSerializer(instance = user, data = request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def information(request):
    user = request.user
    if request.method == 'GET' : 
        infos = Information.objects.filter(user=user)
        serializer = InformationSerializer(infos, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = InformationSerializer(data = request.data)
        if serializer.is_valid():
            info = serializer.save(user=user)
            return Response(InformationSerializer(info).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

User = get_user_model()

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_search(request):
    q = (request.GET.get("q") or "").strip()
    if not q:
        return Response([])

    qs = User.objects.filter(username__icontains=q).order_by("username")[:10]
    return Response([{"id": u.id, "username": u.username} for u in qs])

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import Post, Comment
from .serializers import (
    PostDetailSerializer,
    PostListSerializer,
    CommentSerializer,
)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_list_create(request):
    if request.method == "GET":
        board_type = request.query_params.get("board")
        queryset = (
            Post.objects.all()
            .select_related("author")
            .prefetch_related("comments", "like_users", "dislike_users")
        )
        if board_type in ["product", "card"]:
            queryset = queryset.filter(board_type=board_type)

        serializer = PostListSerializer(queryset, many=True, context={"request": request})
        return Response(serializer.data)

    serializer = PostDetailSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        post = serializer.save(author=request.user)
        data = PostDetailSerializer(post, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticatedOrReadOnly])
def post_detail(request, pk):
    post = get_object_or_404(
        Post.objects.select_related("author").prefetch_related(
            "like_users",
            "dislike_users",
            "comments__author",
            "comments__like_users",
            "comments__dislike_users",
        ),
        pk=pk,
    )

    if request.method == "GET":
        serializer = PostDetailSerializer(post, context={"request": request})
        return Response(serializer.data)

    if not request.user.is_authenticated or request.user != post.author:
        return Response(
            {"detail": "작성자만 수정하거나 삭제할 수 있습니다."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "PATCH":
        serializer = PostDetailSerializer(
            post, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    post.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_post_reaction(request, pk, reaction):
    post = get_object_or_404(Post, pk=pk)
    user = request.user

    if reaction not in ["like", "dislike"]:
        return Response({"detail": "잘못된 반응입니다."}, status=status.HTTP_400_BAD_REQUEST)

    like_set = post.like_users
    dislike_set = post.dislike_users
    current = None

    if reaction == "like":
        if like_set.filter(pk=user.pk).exists():
            like_set.remove(user)
        else:
            like_set.add(user)
            dislike_set.remove(user)
            current = "like"
    else:
        if dislike_set.filter(pk=user.pk).exists():
            dislike_set.remove(user)
        else:
            dislike_set.add(user)
            like_set.remove(user)
            current = "dislike"

    serializer = PostDetailSerializer(post, context={"request": request})
    data = serializer.data
    data["user_reaction"] = current
    return Response(data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticatedOrReadOnly])
def comment_list_create(request, post_pk):
    post = get_object_or_404(Post, pk=post_pk)

    if request.method == "GET":
        comments = post.comments.select_related("author").prefetch_related(
            "like_users", "dislike_users"
        )
        serializer = CommentSerializer(
            comments, many=True, context={"request": request}
        )
        return Response(serializer.data)

    serializer = CommentSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        comment = serializer.save(author=request.user, post=post)
        data = CommentSerializer(comment, context={"request": request}).data
        return Response(data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def comment_detail(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if request.user != comment.author:
        return Response(
            {"detail": "작성자만 수정하거나 삭제할 수 있습니다."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "PATCH":
        serializer = CommentSerializer(
            comment, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    comment.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_comment_reaction(request, pk, reaction):
    comment = get_object_or_404(Comment, pk=pk)
    user = request.user

    if reaction not in ["like", "dislike"]:
        return Response({"detail": "잘못된 반응입니다."}, status=status.HTTP_400_BAD_REQUEST)

    like_set = comment.like_users
    dislike_set = comment.dislike_users
    current = None

    if reaction == "like":
        if like_set.filter(pk=user.pk).exists():
            like_set.remove(user)
        else:
            like_set.add(user)
            dislike_set.remove(user)
            current = "like"
    else:
        if dislike_set.filter(pk=user.pk).exists():
            dislike_set.remove(user)
        else:
            dislike_set.add(user)
            like_set.remove(user)
            current = "dislike"

    serializer = CommentSerializer(comment, context={"request": request})
    data = serializer.data
    data["user_reaction"] = current
    return Response(data)

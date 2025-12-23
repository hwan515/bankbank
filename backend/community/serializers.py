from rest_framework import serializers
from .models import Post, Comment


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    is_author = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "content",
            "author_name",
            "created_at",
            "updated_at",
            "like_count",
            "dislike_count",
            "is_author",
            "user_reaction",
        ]
        read_only_fields = [
            "post",
            "author_name",
            "created_at",
            "updated_at",
            "like_count",
            "dislike_count",
            "is_author",
            "user_reaction",
        ]

    def get_is_author(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        return bool(user and user.is_authenticated and obj.author_id == user.id)

    def get_like_count(self, obj):
        return obj.like_users.count()

    def get_dislike_count(self, obj):
        return obj.dislike_users.count()

    def get_user_reaction(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if user and user.is_authenticated:
            if obj.like_users.filter(pk=user.pk).exists():
                return "like"
            if obj.dislike_users.filter(pk=user.pk).exists():
                return "dislike"
        return None


class PostListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    like_count = serializers.IntegerField(read_only=True)
    dislike_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "board_type",
            "title",
            "author_name",
            "created_at",
            "comment_count",
            "like_count",
            "dislike_count",
        ]

class PostDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source="author.username", read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    is_author = serializers.SerializerMethodField()
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id",
            "board_type",
            "title",
            "content",
            "author_name",
            "created_at",
            "updated_at",
            "is_author",
            "like_count",
            "dislike_count",
            "user_reaction",
            "comments",
        ]
        read_only_fields = [
            "author_name",
            "created_at",
            "updated_at",
            "is_author",
            "like_count",
            "dislike_count",
            "user_reaction",
            "comments",
        ]

    def get_is_author(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        return bool(user and user.is_authenticated and obj.author_id == user.id)

    def get_like_count(self, obj):
        if hasattr(obj, "like_count"):
            return obj.like_count
        return obj.like_users.count()

    def get_dislike_count(self, obj):
        if hasattr(obj, "dislike_count"):
            return obj.dislike_count
        return obj.dislike_users.count()

    def get_user_reaction(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if user and user.is_authenticated:
            if obj.like_users.filter(pk=user.pk).exists():
                return "like"
            if obj.dislike_users.filter(pk=user.pk).exists():
                return "dislike"
        return None

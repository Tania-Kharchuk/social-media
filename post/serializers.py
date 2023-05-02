from rest_framework import serializers

from post.models import Post, Like, Comment
from user.serializers import ProfileSerializer


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = "__all__"

    def validate(self, data):
        like = Like.objects.filter(post_id=data["post"], user_id=data["user"])
        if like:
            raise serializers.ValidationError("You had already liked this post")
        return data


class LikeDetailSerializer(serializers.ModelSerializer):
    post = serializers.CharField(source="post.title", read_only=True)
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Like
        fields = ("id", "post", "user")


class LikeListSerializer(serializers.ModelSerializer):
    post = serializers.CharField(source="post.title", read_only=True)

    class Meta:
        model = Like
        fields = (
            "id",
            "post",
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "post", "user", "content")


class CommentDetailSerializer(serializers.ModelSerializer):
    post = serializers.CharField(source="post.title", read_only=True)
    user = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Comment
        fields = ("id", "post", "user", "content")


class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="user.email", read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "text",
            "media",
            "hashtag",
            "author",
            "likes_count",
            "comments_count",
        )


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("title", "text", "media", "hashtag")


class PostDetailSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)
    likes = LikeDetailSerializer(many=True, read_only=True)
    comments = CommentDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "text",
            "media",
            "hashtag",
            "user",
            "likes",
            "comments",
        )

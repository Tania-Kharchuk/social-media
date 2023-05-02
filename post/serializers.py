from rest_framework import serializers

from post.models import Post, Like
from user.serializers import ProfileSerializer


class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="user.email", read_only=True)
    likes_count = serializers.SerializerMethodField()

    def get_likes_count(self, obj):
        return obj.likes.count()

    class Meta:
        model = Post
        fields = ("id", "title", "text", "media", "hashtag", "author", "likes_count")


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("title", "text", "media", "hashtag")


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


class PostDetailSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)
    likes = LikeDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ("id", "title", "text", "media", "hashtag", "user", "likes")

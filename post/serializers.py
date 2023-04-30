from rest_framework import serializers

from post.models import Post
from user.serializers import ProfileSerializer


class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = Post
        fields = ("id", "title", "text", "media", "hashtag", "author")


class PostCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ("title", "text", "media", "hashtag")


class PostDetailSerializer(serializers.ModelSerializer):
    user = ProfileSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ("id", "title", "text", "media", "hashtag", "user")

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from post.models import Post, Like, Comment
from post.permissions import IsOwnerOrReadOnly
from post.serializers import (
    PostSerializer,
    PostCreateSerializer,
    PostDetailSerializer,
    LikeSerializer,
    CommentSerializer,
    CommentDetailSerializer,
)


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("user")
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        title = self.request.query_params.get("title")
        hashtag = self.request.query_params.get("hashtag")

        queryset = self.queryset.filter(
            Q(user=self.request.user)
            | Q(user__in=self.request.user.following.values("followed_id"))
        )
        if title:
            queryset = queryset.filter(title__icontains=title)

        if hashtag:
            queryset = queryset.filter(hashtag__icontains=hashtag)

        return queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PostDetailSerializer
        if self.action == "create":
            return PostCreateSerializer
        if self.action == "like":
            return LikeSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="like")
    def like(self, request, pk):
        post = get_object_or_404(Post, id=pk)
        user = request.user
        serializer = LikeSerializer(data={"post": post.id, "user": user.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = PostDetailSerializer(post)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="unlike")
    def unlike(self, request, pk):
        post = get_object_or_404(Post, id=pk)
        user = request.user
        like = Like.objects.filter(post=post.id, user=user.id)
        if not like:
            raise ValidationError("You hadn't liked this post yet")
        like.delete()
        response_serializer = PostDetailSerializer(post)
        return Response(response_serializer.data, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.select_related("user", "post")
    permission_classes = (IsOwnerOrReadOnly,)
    serializer_class = CommentSerializer
    lookup_field = "pk"

    def get_queryset(self):
        queryset = self.queryset.filter(
            Q(post_id=self.kwargs.get("post_id"))
            | Q(post__user_id=self.request.user)
            | Q(post__user__in=self.request.user.following.values("followed_id"))
            | Q(user_id=self.request.user)
            | Q(user__in=self.request.user.following.values("followed_id"))
        )

        return queryset

    def get_serializer_class(self):
        if self.action == "create":
            return CommentSerializer
        return CommentDetailSerializer

    def perform_create(self, serializer):
        post = get_object_or_404(Post, pk=self.kwargs.get("post_id"))
        serializer.save(user=self.request.user, post=post)

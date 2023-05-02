from django.contrib.auth import get_user_model
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from drf_spectacular.types import OpenApiTypes
from rest_framework import generics, mixins, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from post.models import Like
from post.serializers import LikeListSerializer
from user.models import Follow

from drf_spectacular.utils import extend_schema, OpenApiParameter

from user.serializers import (
    UserSerializer,
    ProfileSerializer,
    FollowSerializer,
    MyProfileSerializer,
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UpdateUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class MyProfileView(
    generics.RetrieveUpdateAPIView,
    generics.DestroyAPIView,
):
    serializer_class = MyProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_liked_posts(self):
        liked_posts = Like.objects.filter(user=self.request.user).select_related("post")
        liked_posts_serializer = LikeListSerializer(liked_posts, many=True)
        return liked_posts_serializer.data

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        liked_posts_data = self.get_liked_posts()
        data = {
            "profile_data": serializer.data,
            "you_have_liked": liked_posts_data,
        }
        return Response(data)


class ProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = get_user_model().objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the users with filters"""
        nickname = self.request.query_params.get("nickname")
        email = self.request.query_params.get("email")
        queryset = self.queryset

        if nickname:
            queryset = queryset.filter(nickname__icontains=nickname)

        if email:
            queryset = queryset.filter(email__icontains=email)
        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "follow" or self.action == "unfollow":
            return FollowSerializer
        return ProfileSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="follow",
    )
    def follow(self, request, pk):
        """Follow certain user"""
        user_to_follow = get_object_or_404(get_user_model(), id=pk)
        serializer = FollowSerializer(
            data={"follower": self.request.user.id, "followed": user_to_follow.id}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return redirect(reverse("user:my_profile"))

    @action(
        methods=["POST"],
        detail=True,
        url_path="unfollow",
    )
    def unfollow(self, request, pk, *args, **kwargs):
        """Unfollow certain user"""
        user_to_unfollow = get_object_or_404(get_user_model(), id=pk)
        if self.request.user.id != user_to_unfollow.id:
            follow = Follow.objects.filter(
                follower=request.user, followed=user_to_unfollow
            )
            if follow:
                follow.delete()
                return redirect(reverse("user:my_profile"))
            return ValidationError("You are not following this user.")
        return ValidationError("You can't unfollow yourself.")

    def get_object(self):
        if self.kwargs.get("pk") == self.request.user.pk:
            return self.request.user
        return super().get_object()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance == self.request.user:
            return redirect(reverse("user:my_profile"))
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "nickname",
                type=OpenApiTypes.STR,
                description="Filter by nickname (ex. ?nickname=john)",
            ),
            OpenApiParameter(
                "email",
                type=OpenApiTypes.STR,
                description="Filter by email (ex. ?email=john@gmail.com)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

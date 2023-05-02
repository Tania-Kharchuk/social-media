from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import generics, mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from post.models import Like
from post.serializers import LikeDetailSerializer
from user.models import Follow

# from drf_spectacular.utils import extend_schema, OpenApiParameter

from user.serializers import (
    UserSerializer,
    ProfileSerializer,
    FollowSerializer,
    FollowingDetailSerializer,
    FollowersDetailSerializer,
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer


class UpdateUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UpdateProfileView(
    generics.RetrieveUpdateAPIView,
    generics.DestroyAPIView,
):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def get_followers(self):
        followers = Follow.objects.filter(followed=self.request.user).select_related(
            "follower"
        )
        follower_serializer = FollowersDetailSerializer(followers, many=True)
        return follower_serializer.data

    def get_following(self):
        following = Follow.objects.filter(follower=self.request.user).select_related(
            "followed"
        )
        following_serializer = FollowingDetailSerializer(following, many=True)
        return following_serializer.data

    def get_liked_posts(self):
        liked_posts = Like.objects.filter(user=self.request.user).select_related("post")
        liked_posts_serializer = LikeDetailSerializer(liked_posts, many=True)
        return liked_posts_serializer.data

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        follower_data = self.get_followers()
        following_data = self.get_following()
        liked_posts_data = self.get_liked_posts()
        data = {
            "profile_data": serializer.data,
            "followers": follower_data,
            "following": following_data,
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

        queryset = self.queryset

        if nickname:
            queryset = queryset.filter(nickname__icontains=nickname)

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
        user_to_follow = get_user_model().objects.get(id=pk)
        if self.request.user.id != user_to_follow.id:
            follow = Follow.objects.filter(
                follower=request.user, followed=user_to_follow
            )
            if follow:
                message = "You are already following this user."
                return Response(
                    {"message": message},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            Follow.objects.create(follower=request.user, followed=user_to_follow)
            return redirect(reverse("user:my_profile"))
        message = "You can't follow yourself."
        return Response(
            {"message": message},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(
        methods=["POST"],
        detail=True,
        url_path="unfollow",
    )
    def unfollow(self, request, pk, *args, **kwargs):
        user_to_unfollow = get_user_model().objects.get(id=pk)
        if self.request.user.id != user_to_unfollow.id:
            follow = Follow.objects.filter(
                follower=request.user, followed=user_to_unfollow
            )
            if follow:
                follow.delete()
                return redirect(reverse("user:my_profile"))
            message = "You are not following this user."
            return Response(
                {"message": message},
                status=status.HTTP_200_OK,
            )
        message = "You can't unfollow yourself."
        return Response(
            {"message": message},
            status=status.HTTP_400_BAD_REQUEST,
        )

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

    # @extend_schema(
    #     parameters=[
    #         OpenApiParameter(
    #             "nickname",
    #             type=OpenApiTypes.STR,
    #             description="Filter by nickname (ex. ?title=user)",
    #         ),
    #     ]
    # )
    # def list(self, request, *args, **kwargs):
    #     return super().list(request, *args, **kwargs)

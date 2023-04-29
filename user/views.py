from django.contrib.auth import get_user_model
from rest_framework import generics, mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

# from drf_spectacular.utils import extend_schema, OpenApiParameter

from user.serializers import (
    UserSerializer,
    ProfileUpdateSerializer,
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
    serializer_class = ProfileUpdateSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class ProfileViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = get_user_model().objects.all()
    serializer_class = ProfileUpdateSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the movies with filters"""
        nickname = self.request.query_params.get("nickname")

        queryset = self.queryset

        if nickname:
            queryset = queryset.filter(nickname__icontains=nickname)

        return queryset.distinct()

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

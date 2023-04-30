from django.db.models import Q
from rest_framework import viewsets


from post.models import Post
from post.permissions import IsOwnerOrReadOnly
from post.serializers import PostSerializer, PostCreateSerializer, PostDetailSerializer


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

        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

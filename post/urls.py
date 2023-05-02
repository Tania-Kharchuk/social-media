from django.urls import path, include
from rest_framework import routers

from post.views import PostViewSet, CommentViewSet

router = routers.DefaultRouter()
router.register("", PostViewSet)
router.register("", CommentViewSet)
app_name = "post"

urlpatterns = [
    path("", include(router.urls)),
    path("<int:pk>/like/", PostViewSet.as_view({"post": "like"}), name="like"),
    path("<int:pk>/unlike/", PostViewSet.as_view({"post": "unlike"}), name="unlike"),
    path(
        "<int:post_id>/comment/",
        CommentViewSet.as_view({"get": "list", "post": "create"}),
        name="comment",
    ),
    path(
        "<int:post_id>/comment/<int:pk>/",
        CommentViewSet.as_view(
            {"get": "retrieve", "delete": "destroy", "put": "update", "patch": "update"}
        ),
        name="comment-detail",
    ),
]

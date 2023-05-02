from django.urls import path, include
from rest_framework import routers

from post.views import PostViewSet

router = routers.DefaultRouter()
router.register("", PostViewSet)
app_name = "post"

urlpatterns = [
    path("", include(router.urls)),
    path("<int:pk>/like/", PostViewSet.as_view({"post": "like"}), name="like"),
    path("<int:pk>/unlike/", PostViewSet.as_view({"post": "unlike"}), name="unlike"),
]

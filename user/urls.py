from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

from user.views import CreateUserView, UpdateUserView, UpdateProfileView, ProfileViewSet

router = routers.DefaultRouter()
router.register("", ProfileViewSet)
app_name = "user"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path(
        "my-profile/",
        UpdateProfileView.as_view(),
        name="my_profile",
    ),
    path(
        "my-profile/change-password",
        UpdateUserView.as_view(),
        name="change-password",
    ),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("", include(router.urls)),
]

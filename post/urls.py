from rest_framework import routers

from post.views import PostViewSet

router = routers.DefaultRouter()
router.register("", PostViewSet)
app_name = "post"

urlpatterns = router.urls

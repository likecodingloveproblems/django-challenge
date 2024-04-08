from django.conf import settings
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from matchticketselling.users.api.views import UserViewSet

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)

app_name = "api"
urlpatterns = [
    *router.urls,
    path(
        "stadium-management/",
        include("stadium_management.urls", namespace="stadium_management"),
    ),
    path("accounting/", include("accounting.urls", namespace="accounting")),
]

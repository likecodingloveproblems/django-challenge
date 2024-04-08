from django.conf import settings
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

from stadium_management.views import MatchViewSet
from stadium_management.views import SeatViewSet
from stadium_management.views import StadiumViewSet

app_name = "stadium_management"

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("stadium", StadiumViewSet)
router.register("match", MatchViewSet)
router.register("seat", SeatViewSet)

urlpatterns = [
    *router.urls,
]

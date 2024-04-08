from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from stadium_management.models import Match
from stadium_management.models import Seat
from stadium_management.models import Stadium
from stadium_management.permissions import IsAdminAndNotReservedOrReadOnly
from stadium_management.permissions import IsAdminUserOrReadOnly
from stadium_management.serializers import MatchSerializer
from stadium_management.serializers import SeatSerializer
from stadium_management.serializers import StadiumSerializer


class StadiumViewSet(viewsets.ModelViewSet):
    queryset = Stadium.objects.all()
    serializer_class = StadiumSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                description="Name of stadium",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="description",
                description="Description of stadium can include address,"
                "and some other information about the stadium",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="loggo",
                description="Loggo of stadium",
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name="capacity",
                description="Capacity shows how many seat has this stadium",
                required=True,
                type=int,
            ),
        ],
        description="Create a new stadium",
        responses={201: StadiumSerializer(), 400: None},
        examples=[
            OpenApiExample(
                "Example 1",
                description="Azadi volly ball stadium",
                value={
                    "name": "azadi",
                    "description": """azadi volly ball stadium was created in 1980
                    by <NAME> with 1000 seats capacity,
                    It's the biggest stadium in iran!
                    Address: "azadi volly ball"
                    """,
                    "capacity": 1000,
                },
                status_codes=[status.HTTP_201_CREATED],
            ),
        ],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class MatchViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="host_team",
                description="ID of the host team",
                required=True,
                type=int,
            ),
            OpenApiParameter(
                name="guest_team",
                description="ID of the guest team",
                required=True,
                type=int,
            ),
            OpenApiParameter(
                name="stadium",
                description="ID of the stadium",
                required=True,
                type=int,
            ),
            OpenApiParameter(
                name="datetime",
                description="Datetime that game start at that time",
                required=True,
                type=OpenApiTypes.DATETIME,
            ),
            OpenApiParameter(
                name="does_create_seats",
                description="Do you want to create all the seats automatically?",
                required=False,
                type=bool,
            ),
        ],
        description="Create a new match",
        responses={201: MatchSerializer(), 400: None},
    )
    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create a new match and create seats if user want

        :param request: rest_framework Http request object
        :type request: Request
        :return: http response object
        :rtype: Response
        """
        return super().create(request, *args, **kwargs)


class SeatViewSet(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    serializer_class = SeatSerializer
    permission_classes = [IsAdminAndNotReservedOrReadOnly]

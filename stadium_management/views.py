from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework import viewsets

from stadium_management.models import Stadium
from stadium_management.permissions import IsAdminUserOrReadOnly
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
        responses={201: StadiumSerializer()},
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

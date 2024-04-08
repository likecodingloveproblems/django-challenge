from drf_spectacular.utils import OpenApiExample
from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from stadium_management.serializers import StadiumSerializer


class StadiumAddView(APIView):
    """
    Adding a new stadium
    """

    permission_classes = [IsAdminUser]
    serializer_class = StadiumSerializer

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
    def post(self, request: Request) -> Response:
        """
        Create a new stadium.

        :param request: The HTTP request object.
        :type request: Request
        :return: The HTTP response object.
        :type: Response
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )

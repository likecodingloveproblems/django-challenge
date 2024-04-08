from drf_spectacular.utils import OpenApiParameter
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from matchticketselling.users.models import User
from matchticketselling.users.serializers import SignupSerializer


class SignupView(APIView):
    """
    View for user registration and account creation.
    """

    permission_classes = [AllowAny]
    serializer_class = SignupSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="username",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="password",
                required=True,
                type=str,
            ),
            OpenApiParameter(
                name="duplicate_password",
                required=True,
                type=str,
            ),
        ],
        responses={
            201: {"token": "key"},
            400: None,
        },
    )
    def post(self, request: Request) -> Response:
        """
        Create a new user account

        :param request: HTTP request object.
        :type request: Request
        :return: HTTP response object.
        :rtype: Response
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = self._get_token(user)
        return Response(
            data={"token": token.key},
            status=status.HTTP_201_CREATED,
        )

    @staticmethod
    def _get_token(user: User) -> Token:
        """
        Get or create token for the User
        :param user: User object
        :type user: User
        :return: token object
        :rtype: Token
        """
        token, _ = Token.objects.get_or_create(user=user)
        return token

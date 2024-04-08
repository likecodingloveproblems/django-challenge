from rest_framework import serializers

from matchticketselling.users.exceptions import PasswordsAreNotEqualError
from matchticketselling.users.exceptions import UsernameAlreadyExistsError
from matchticketselling.users.models import User


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True, required=True)
    password = serializers.CharField(write_only=True, required=True)
    duplicate_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["username", "password", "duplicate_password"]

    def validate_username(self, value: str) -> str:
        """
        Check username exists
        :param value: username value
        :type value: str
        :return: username value
        :rtype: str
        """
        if User.objects.filter(username=value).exists():
            raise UsernameAlreadyExistsError
        return value

    def validate(self, data: dict) -> dict:
        """
        Validate duplicate password is equal to the original password

        :param data: form data
        :type data: dict
        :return: form data
        :rtype: dict
        """
        if data["password"] != data["duplicate_password"]:
            raise PasswordsAreNotEqualError
        return data

    def create(self, validated_data):
        """
        User creation need to hash password and normalize username and password

        :param validated_data: validated data
        :type validated_data: dict
        :return: User object
        :rtype: User
        """
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
        )

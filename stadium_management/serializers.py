from rest_framework import serializers

from stadium_management.models import Match
from stadium_management.models import Stadium


class StadiumSerializer(serializers.ModelSerializer):
    """
    Stadium CRUD operations serializer
    """

    class Meta:
        model = Stadium
        fields = ["id", "name", "description", "logo", "capacity"]
        extra_kwargs = {"logo": {"required": False, "allow_null": True}}


class MatchSerializer(serializers.ModelSerializer):
    """
    Match CRUD operations serializer
    """

    does_create_seats = serializers.BooleanField(
        write_only=True,
        required=False,
        default=True,
    )

    class Meta:
        model = Match
        fields = [
            "id",
            "host_team",
            "guest_team",
            "stadium",
            "datetime",
            "does_create_seats",
        ]

    def create(self, validated_data: dict) -> Match:
        """
        Create a new match
        if the does_create_seats is set to True, will create match's seats
        :param validated_data: validated data dictionary
        :type validated_data: dict
        :return: created match obj
        :rtype: Match
        """
        does_create_seats = validated_data.pop("does_create_seats", None)
        obj: Match = super().create(validated_data)
        if does_create_seats:
            obj.create_seats()
        return obj

from rest_framework import serializers

from stadium_management.models import Stadium


class StadiumSerializer(serializers.ModelSerializer):
    """
    Serializer to be used for the Stadium creation
    """

    class Meta:
        model = Stadium
        fields = ["name", "description", "logo", "capacity"]
        extra_kwargs = {"logo": {"required": False, "allow_null": True}}

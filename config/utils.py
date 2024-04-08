from django.db import models
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class OkResponse(Response):
    """
    Return the ok response with status code 200
    """

    def __init__(
        self,
        data="Request was successful",
        status=status.HTTP_200_OK,
        *args,
        **kwargs,
    ):
        super().__init__(*args, data=data, status=status, **kwargs)

from django.db import models
from django.db.models import Model
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from rest_framework import status
from rest_framework.response import Response

from matchticketselling.users.models import User


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


class AdminTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_superuser(username="test")
        self.client.force_login(user=self.user)


class BaseTestCase:
    model: Model
    list_namespace: str
    detail_namespace: str

    def setUp(self):
        self.normal_user = User.objects.create_user(username="username1")
        self.super_user = User.objects.create_superuser(username="username2")
        self.client.force_authenticate(self.super_user)

    def get_list_url(self):
        return reverse(self.list_namespace)

    def get_detail_url(self, kwargs: dict) -> str:
        return reverse(self.detail_namespace, kwargs=kwargs)

    def get_update_data(self) -> dict:
        raise NotImplementedError

    def get_create_data(self) -> dict:
        raise NotImplementedError

    def get_partial_update_data(self) -> dict:
        raise NotImplementedError

    def test_list_view(self):
        response = self.client.get(self.get_list_url())
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_view(self):
        obj = baker.make(self.model)
        response = self.client.get(self.get_detail_url({"pk": obj.id}))
        assert response.status_code == status.HTTP_200_OK

    def test_update_view(self, status_code=status.HTTP_200_OK):
        obj = baker.make(self.model)
        response = self.client.put(
            self.get_detail_url({"pk": obj.id}),
            self.get_update_data(),
        )
        assert response.status_code == status_code

    def test_partial_update_view(self, status_code=status.HTTP_200_OK):
        obj = baker.make(self.model)
        response = self.client.patch(
            self.get_detail_url({"pk": obj.id}),
            self.get_partial_update_data(),
        )
        assert response.status_code == status_code

    def test_create_view(self, status_code=status.HTTP_201_CREATED, data=None):
        response = self.client.post(
            self.get_list_url(),
            data if data else self.get_create_data(),
        )
        assert response.status_code == status_code
        if status_code == status.HTTP_201_CREATED:
            assert self.model.objects.filter(**self.get_create_data()).exists()

    def test_successful_delete(self):
        obj = baker.make(self.model)
        response = self.client.delete(self.get_detail_url({"pk": obj.id}))
        assert response.status_code == status.HTTP_204_NO_CONTENT

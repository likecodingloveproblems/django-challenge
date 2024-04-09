from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from config.utils import BaseTestCase
from stadium_management.models import Stadium


class StadiumViewSetTest(BaseTestCase, APITestCase):
    model = Stadium
    list_namespace = "api:stadium_management:stadium-list"
    detail_namespace = "api:stadium_management:stadium-detail"

    def get_create_data(self) -> dict:
        return {"name": "name", "description": "description", "capacity": 10}

    def get_update_data(self) -> dict:
        return {"name": "new name", "description": "new description", "capacity": 10}

    def get_partial_update_data(self) -> dict:
        return {"name": "new name"}

    def test_empty_name_is_not_allowed(self):
        response = self.client.post(
            reverse("api:stadium_management:stadium-list"),
            data={"name": "", "description": "description", "capacity": 10},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert not Stadium.objects.filter(name="name", capacity=10).exists()

from http import HTTPStatus

from django.urls import reverse

from stadium_management.models import Stadium
from stadium_management.models import Team


class TestStadiumAdmin:
    def test_changelist(self, admin_client):
        url = reverse("admin:stadium_management_stadium_changelist")
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_add(self, admin_client):
        url = reverse("admin:stadium_management_stadium_add")
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK

        response = admin_client.post(
            url,
            data={
                "name": "name",
                "description": "description",
                "capacity": 1000,
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert Stadium.objects.filter(name="name").exists()

    def test_view_stadium(self, admin_client):
        stadium = Stadium.objects.create(name="name", description="", capacity=1)
        url = reverse(
            "admin:stadium_management_stadium_change",
            kwargs={"object_id": stadium.pk},
        )
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK


class TestTeamAdmin:
    def test_changelist(self, admin_client):
        url = reverse("admin:stadium_management_team_changelist")
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_add(self, admin_client):
        url = reverse("admin:stadium_management_team_add")
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK

        response = admin_client.post(
            url,
            data={
                "name": "name",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert Team.objects.filter(name="name").exists()

    def test_view_stadium(self, admin_client):
        team = Team.objects.create(name="name")
        url = reverse(
            "admin:stadium_management_team_change",
            kwargs={"object_id": team.pk},
        )
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK

from http import HTTPStatus

from django.urls import reverse
from model_bakery import baker

from stadium_management.models import Match
from stadium_management.models import Seat
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

    def test_view_team(self, admin_client):
        team = Team.objects.create(name="name")
        url = reverse(
            "admin:stadium_management_team_change",
            kwargs={"object_id": team.pk},
        )
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK


class TestMatchAdmin:
    def test_changelist(self, admin_client):
        url = reverse("admin:stadium_management_match_changelist")
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_add(self, admin_client):
        url = reverse("admin:stadium_management_match_add")
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK
        host_team = baker.make(Team, id=1)
        guest_team = baker.make(Team, id=2)
        stadium = baker.make(Stadium, id=1, capacity=2)
        response = admin_client.post(
            url,
            data={
                "host_team": 1,
                "guest_team": 2,
                "stadium": 1,
                "datetime_0": "2024-01-01",
                "datetime_1": "20:30",
                "seat_price": 10_000,
                "does_create_seats": "on",
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        match = Match.objects.filter(
            host_team=host_team,
            guest_team=guest_team,
            stadium=stadium,
        ).first()
        assert match is not None
        seats = Seat.objects.filter(match=match)
        assert seats.count() == stadium.capacity
        assert seats.first().price == match.seat_price

    def test_view_match(self, admin_client):
        match = baker.make(Match)
        url = reverse(
            "admin:stadium_management_match_change",
            kwargs={"object_id": match.pk},
        )
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK


class TestSeatAdmin:
    def test_changelist(self, admin_client):
        url = reverse("admin:stadium_management_seat_changelist")
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK

    def test_add(self, admin_client):
        url = reverse("admin:stadium_management_seat_add")
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK
        match = baker.make(Match, id=1)
        response = admin_client.post(
            url,
            data={
                "number": 1,
                "match": 1,
                "price": 1000,
            },
        )
        assert response.status_code == HTTPStatus.FOUND
        assert Seat.objects.filter(number=1, match=match, price=1000).exists()

    def test_view_seat(self, admin_client):
        seat = baker.make(Seat)
        url = reverse(
            "admin:stadium_management_seat_change",
            kwargs={"object_id": seat.pk},
        )
        response = admin_client.get(url)
        assert response.status_code == HTTPStatus.OK

from datetime import datetime

from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from config.utils import BaseTestCase
from stadium_management.models import Match
from stadium_management.models import Seat
from stadium_management.models import Stadium
from stadium_management.models import Team


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


class MatchViewSetTest(BaseTestCase, APITestCase):
    model = Match
    list_namespace = "api:stadium_management:match-list"
    detail_namespace = "api:stadium_management:match-detail"

    def setUp(self):
        super().setUp()
        self.stadium = baker.make(Stadium, id=1, capacity=5)
        self.host_team = baker.make(Team, id=1)
        self.guest_team = baker.make(Team, id=2)
        self.datetime = datetime(
            2024,
            1,
            1,
            12,
            30,
            tzinfo=timezone.get_current_timezone(),
        )
        self.seat_price = 1000
        self.match = Match.objects.create(
            stadium=self.stadium,
            host_team=self.host_team,
            guest_team=self.guest_team,
            datetime=self.datetime,
            seat_price=self.seat_price,
        )

    def get_create_data(self) -> dict:
        return {
            "stadium": 1,
            "host_team": 1,
            "guest_team": 2,
            "datetime": datetime(
                2024,
                1,
                1,
                20,
                30,
                tzinfo=timezone.get_current_timezone(),
            ),
            "seat_price": 900,
        }

    def get_update_data(self) -> dict:
        return {
            "stadium": 1,
            "host_team": 1,
            "guest_team": 2,
            "datetime": datetime(
                2024,
                1,
                2,
                20,
                30,
                tzinfo=timezone.get_current_timezone(),
            ),
            "seat_price": 800,
        }

    def get_partial_update_data(self) -> dict:
        return {"seat_price": 2000}

    def test_update_view(self):
        super().test_update_view(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_partial_update_view(self):
        super().test_partial_update_view(status_code=status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_overlapped_match_is_not_allowed(self):
        test_table = [
            {
                "stadium": 1,
                "host_team": 1,
                "guest_team": 2,
                "datetime": datetime(
                    2024,
                    1,
                    1,
                    14,
                    29,
                    tzinfo=timezone.get_current_timezone(),
                ),
                "seat_price": 900,
            },
            {
                "stadium": 1,
                "host_team": 1,
                "guest_team": 2,
                "datetime": datetime(
                    2024,
                    1,
                    1,
                    10,
                    31,
                    tzinfo=timezone.get_current_timezone(),
                ),
                "seat_price": 900,
            },
        ]

        for case in test_table:
            self.test_create_view(status_code=status.HTTP_400_BAD_REQUEST, data=case)

    def test_seats_created(self):
        self.test_create_view()
        assert Seat.objects.count() == self.stadium.capacity

    def test_deos_not_create_seats(self):
        data = self.get_create_data()
        data["does_create_seats"] = False
        self.test_create_view(data=data)
        assert not Seat.objects.exists()


class SeatViewSetTest(BaseTestCase, APITestCase):
    model = Seat
    list_namespace = "api:stadium_management:seat-list"
    detail_namespace = "api:stadium_management:seat-detail"

    def setUp(self):
        super().setUp()
        self.stadium = baker.make(Stadium, capacity=5)
        self.match = baker.make(Match, id=1, stadium=self.stadium)
        self.seat = baker.make(Seat, id=1, match=self.match, number=1)
        self.reserved_seat = baker.make(
            Seat,
            id=2,
            match=self.match,
            number=2,
            is_reserved=True,
            full_name="Jon Doe",
        )

    def get_create_data(self) -> dict:
        return {"number": 3, "match": 1, "price": 1000}

    def get_update_data(self) -> dict:
        return {"number": 4, "match": 1, "price": 2000}

    def get_partial_update_data(self) -> dict:
        return {"price": 3000}

    def test_can_not_update_reserved_seats(self):
        response = self.client.patch(
            self.get_detail_url({"pk": 2}),
            {"price": 10_000},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

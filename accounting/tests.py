from datetime import datetime

from django.urls import reverse
from django.utils import timezone
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from accounting.models import Invoice
from accounting.models import InvoiceItem
from matchticketselling.users.models import User
from stadium_management.models import Match
from stadium_management.models import Seat
from stadium_management.models import Stadium
from stadium_management.models import Team


class BaseAuthenticatedUserAPITestCase(APITestCase):
    namespace: str

    def setUp(self):
        self.user = User.objects.create_user(username="username")
        self.client.force_authenticate(user=self.user)

    def get_url(self, *args, **kwargs):
        return reverse(self.namespace, *args, **kwargs)


class InvoiceViewTest(BaseAuthenticatedUserAPITestCase):
    namespace = "api:accounting:invoice"

    def get_url(self, invoice_id: int):
        return reverse(self.namespace, kwargs={"invoice_id": invoice_id})

    def setUp(self):
        super().setUp()
        self.stadium = baker.make(Stadium, name="azadi")
        self.host_team = baker.make(Team, name="team1")
        self.guest_team = baker.make(Team, name="team2")
        self.match = baker.make(
            Match,
            stadium=self.stadium,
            host_team=self.host_team,
            guest_team=self.guest_team,
            datetime=datetime(
                2024,
                1,
                1,
                21,
                30,
                tzinfo=timezone.get_current_timezone(),
            ),
            seat_price=1000,
        )
        self.seat = baker.make(
            Seat,
            number=1,
            match=self.match,
            is_reserved=True,
            full_name="Jon Smith",
            price=1000,
        )
        self.invoice = baker.make(Invoice, id=1, user=self.user, total_price=1000)
        self.item = baker.make(
            InvoiceItem,
            invoice=self.invoice,
            seat=self.seat,
            full_name="Jon Smith",
        )
        other = User.objects.create(username="other")
        self.invalid_invoice = baker.make(Invoice, id=2, user=other)

    def test_get_invoice_view(self):
        response = self.client.get(self.get_url(1))
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "status": "Pending",
            "total_price": 1000,
            "paid_at": None,
            "items": [
                {
                    "full_name": "Jon Smith",
                    "seat": {
                        "number": 1,
                        "price": 1000,
                        "match_name": "team1:team2 at 2024-01-01 21:30:00+00:00"
                        " in azadi",
                    },
                },
            ],
        }

    def test_not_found(self):
        response = self.client.get(self.get_url(3))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_not_owned_invoice(self):
        response = self.client.get(self.get_url(2))
        assert response.status_code == status.HTTP_403_FORBIDDEN


class AddInvoiceItemViewTest(BaseAuthenticatedUserAPITestCase):
    namespace = "api:accounting:add-invoice-item"

    def setUp(self):
        super().setUp()
        self.seat = baker.make(Seat, id=1, is_reserved=False)
        self.reserved_seat = baker.make(
            Seat,
            id=2,
            is_reserved=True,
            full_name="full name",
        )

    def test_add_item_when_there_is_not_invoice(self):
        response = self.client.post(
            self.get_url(),
            data={
                "seat": self.seat.id,
                "full_name": "Jon Smith",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        self.seat.refresh_from_db()
        assert self.seat.full_name == "Jon Smith"
        assert self.seat.is_reserved
        invoice = Invoice.objects.get(user=self.user)
        assert invoice.total_price == self.seat.price

    def test_add_item_when_there_is_reserved(self):
        baker.make(Invoice, id=1, user=self.user)
        response = self.client.post(
            self.get_url(),
            data={
                "seat": self.seat.id,
                "full_name": "Jon Smith",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED

    def test_can_not_add_reserved_seat(self):
        response = self.client.post(
            self.get_url(),
            data={
                "seat": self.reserved_seat.id,
                "full_name": "Jon Smith",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_seat_not_found(self):
        response = self.client.post(
            self.get_url(),
            data={
                "seat": 3,
                "full_name": "Jon Smith",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["seat"][0].code == "does_not_exist"


class RemoveItemFromInvoiceViewTest(BaseAuthenticatedUserAPITestCase):
    namespace = "api:accounting:remove-invoice-item"

    def setUp(self):
        super().setUp()
        self.match = baker.make(Match)
        self.seat1 = baker.make(Seat, match=self.match, number=1, price=1000)
        self.seat2 = baker.make(Seat, match=self.match, number=2, price=2000)
        self.invoice = baker.make(Invoice, user=self.user, total_price=3000)
        self.item1 = baker.make(InvoiceItem, invoice=self.invoice, seat=self.seat1)
        self.item2 = baker.make(InvoiceItem, invoice=self.invoice, seat=self.seat2)
        self.invoice.save(update_fields=["total_price"])

    def test_remove_one_item(self):
        response = self.client.delete(self.get_url(kwargs={"item_id": self.item1.id}))
        assert response.status_code == status.HTTP_200_OK
        assert self.invoice.invoiceitem_set.count() == 1
        assert self.invoice.invoiceitem_set.first().id == self.item2.id

    def test_invoice_deleted_when_has_not_item(self):
        for item_id in InvoiceItem.objects.values_list("id", flat=True):
            response = self.client.delete(self.get_url(kwargs={"item_id": item_id}))
            assert response.status_code == status.HTTP_200_OK
        assert not Invoice.objects.exists()


class PayInvoiceView(BaseAuthenticatedUserAPITestCase):
    namespace = "api:accounting:pay-invoice"

    def setUp(self):
        super().setUp()
        self.invoice = baker.make(
            Invoice,
            user=self.user,
            paid_at=None,
            status=Invoice.InvoiceStatus.PENDING,
        )

    def test_pay_invoice(self):
        response = self.client.post(
            self.get_url(kwargs={"invoice_id": self.invoice.id}),
        )
        assert response.status_code == status.HTTP_200_OK
        self.invoice.refresh_from_db()
        assert self.invoice.paid_at is not None
        assert self.invoice.status == Invoice.InvoiceStatus.PAID

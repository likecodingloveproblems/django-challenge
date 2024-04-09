from django.urls import reverse
from model_bakery import baker
from rest_framework import status
from rest_framework.test import APITestCase

from accounting.models import Invoice
from accounting.models import InvoiceItem
from matchticketselling.users.models import User


class BaseAuthenticatedUserAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="username")
        self.client.force_authenticate(user=self.user)


class InvoiceViewTest(BaseAuthenticatedUserAPITestCase):
    namespace = "api:accounting:invoice"

    def get_url(self, invoice_id: int):
        return reverse(self.namespace, kwargs={"invoice_id": invoice_id})

    def setUp(self):
        super().setUp()
        self.invoice = baker.make(Invoice, id=1, user=self.user)
        self.item = baker.make(InvoiceItem, invoice=self.invoice)
        other = User.objects.create(username="other")
        self.invalid_invoice = baker.make(Invoice, id=2, user=other)

    def test_get_invoice_view(self):
        response = self.client.get(self.get_url(1))
        assert response.status_code == status.HTTP_200_OK

    def test_not_found(self):
        response = self.client.get(self.get_url(3))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_not_owned_invoice(self):
        response = self.client.get(self.get_url(2))
        assert response.status_code == status.HTTP_403_FORBIDDEN

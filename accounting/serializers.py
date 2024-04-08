from django.db import transaction
from rest_framework import serializers

from accounting.exceptions import AlreadyReservedSeatError
from accounting.exceptions import OnlyPendingInvoice
from accounting.models import Invoice
from accounting.models import InvoiceItem
from stadium_management.models import Seat


class SeatSerializer(serializers.ModelSerializer):
    match_name = serializers.SerializerMethodField()

    class Meta:
        model = Seat
        fields = ["number", "price", "match_name"]

    def get_match_name(self, obj: Seat) -> str:
        """Return seat match name"""
        return str(obj.match)


class InvoiceItemSerializer(serializers.ModelSerializer):
    seat = SeatSerializer(read_only=True)

    class Meta:
        model = InvoiceItem
        fields = ["full_name", "seat"]


class InvoiceSerializer(serializers.ModelSerializer):
    items = InvoiceItemSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = ["status", "total_price", "paid_at", "items"]


class AddInvoiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceItem
        fields = ["seat", "full_name"]

    @property
    def _user(self):
        return self.context["request"].user

    def create(self, validated_data):
        """
        Create Invoice Item
        we can have a mechanisem to reserve the seat for this user for 10 minutes and
        Then if the user pay this invoice, it's finalized and
        If the user does not reserve the invoice it will be expired.
        :param validated_data:
        :type validated_data:
        :return:
        :rtype:
        """
        with transaction.atomic():
            seat = validated_data.pop("seat")
            try:
                seat = Seat.objects.select_for_update().get_object_or_404(
                    Seat,
                    id=seat.id,
                    is_reserved=False,
                )
            except Seat.DoesNotExist:
                raise AlreadyReservedSeatError  # noqa: B904
            seat.is_reserved = True
            seat.save(update_fields=["is_reserved"])
            try:
                invoice = Invoice.objects.get(
                    status=Invoice.InvoiceStatus.PENDING,
                    user=self._user,
                )
            except Invoice.DoesNotExist:
                raise OnlyPendingInvoice  # noqa: B904
            return InvoiceItem.objects.create(invoice=invoice, **validated_data)

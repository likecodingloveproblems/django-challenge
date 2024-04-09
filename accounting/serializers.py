from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from accounting.exceptions import AlreadyReservedSeatError
from accounting.exceptions import ProcessFailed
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
    items = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ["status", "total_price", "paid_at", "items"]

    def get_items(self, obj: Invoice) -> dict:
        return InvoiceItemSerializer(obj.invoiceitem_set.all(), many=True).data

    def get_status(self, obj: Invoice) -> str:
        return obj.get_status_display()


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
            seat: Seat = get_object_or_404(Seat.objects.select_for_update(), id=seat.id)
            if seat.is_reserved:
                raise AlreadyReservedSeatError
            seat.is_reserved = True
            seat.full_name = validated_data["full_name"]
            seat.save(update_fields=["is_reserved", "full_name"])
            invoice, _ = Invoice.objects.get_or_create(
                status=Invoice.InvoiceStatus.PENDING,
                user=self._user,
            )
            invoice.total_price += seat.price
            invoice.save(update_fields=["total_price"])
            return InvoiceItem.objects.create(
                invoice=invoice,
                seat=seat,
                **validated_data,
            )
        raise ProcessFailed

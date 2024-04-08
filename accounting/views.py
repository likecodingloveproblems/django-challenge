from django.db import transaction
from django.db.models import F
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from accounting.exceptions import OnlyInvoiceOwner
from accounting.models import Invoice
from accounting.models import InvoiceItem
from accounting.serializers import AddInvoiceItemSerializer
from accounting.serializers import InvoiceSerializer
from config.utils import OkResponse


class InvoiceView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceSerializer

    def get(self, request: Request, invoice_id: int) -> Response:
        """
        Show user's invoice

        :param request: request object
        :type request: Request
        :param invoice_id: invoice id
        :type invoice_id: int
        :return: response object
        :rtype: Response
        """
        invoice = get_object_or_404(
            Invoice.objects.select_related("invoiceitem_set__seat__match"),
            id=invoice_id,
        )
        if invoice.user_id != request.user.id:
            raise OnlyInvoiceOwner
        serializer = self.serializer_class(invoice)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class AddInvoiceItemView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AddInvoiceItemSerializer

    def post(self, request):
        """
        Adding item to invoice

        :param request: request object
        :type request: Request
        :return: response object
        :rtype: Response
        """
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data=serializer.data,
            status=status.HTTP_201_CREATED,
        )


class RemoveItemFromInvoiceView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        """
        Removing item from invoice

        :param request: request object
        :type request: Request
        :param item_id: invoice item id
        :type item_id: int
        :return: response object
        :rtype: Response
        """
        with transaction.atomic():
            item: InvoiceItem = get_object_or_404(
                InvoiceItem.objects.select_related("invoice", "seat"),
                id=item_id,
            )
            item.seat.is_reserved = False
            item.seat.save(update_fields=["is_reserved"])
            invoice = item.invoice
            invoice.total_price = F("total_price") - item.seat.price
            invoice.save(update_fields=["total_price"])
            item.delete()
        return OkResponse()


class PayInvoiceView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = InvoiceSerializer

    def post(self, request, invoice_id):
        """
        Pay invoice
        :param request: request object
        :type request: Request
        :param invoice_id: invoice id
        :type invoice_id: int
        :return: response object
        :rtype: Response
        """
        invoice: Invoice = get_object_or_404(
            Invoice.objects.select_related("invoiceitem_set__seat__match").filter(
                status=Invoice.InvoiceStatus.PENDING,
            ),
            id=invoice_id,
        )
        if invoice.user_id != request.user.id:
            raise OnlyInvoiceOwner
        invoice.pay()
        invoice.refresh_from_db()
        serializer = self.serializer_class(invoice)
        return Response(serializer.data, status=status.HTTP_200_OK)

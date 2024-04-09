from datetime import timedelta

from django.db import transaction
from django.db.models import OuterRef
from django.db.models import Subquery
from django.db.models import Sum
from django.utils import timezone

from accounting.models import Invoice
from accounting.models import InvoiceItem


def expire_inactive_invoice_items():
    # TODO: it must be setup in celery as periodic task to be run each 5 minutes
    """
    This celery task check invoices and expire inactive invoice items after 10 minutes
    and make seat free
    :return: Nothing
    :rtype: None
    """
    with transaction.atomic():
        invoices = Invoice.objects.filter(status=Invoice.InvoiceStatus.PENDING)
        items = InvoiceItem.objects.filter(
            invoice__in=Subquery(invoices.values("id")),
            created_at__lte=timezone.now() - timedelta(minutes=10),
        )
        items.update(expired=True)
        invoices.update(
            total_price=Subquery(
                InvoiceItem.objects.filter(invoice_id=OuterRef("id"), expired=False)
                .annotate(total_price=Sum("seat__price"))
                .values("total_price"),
            ),
        )

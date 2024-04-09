from django.db import models
from django.db.models import CheckConstraint
from django.db.models import Q
from django.db.models import UniqueConstraint
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from config.utils import TimeStampedModel
from matchticketselling.users.models import User
from stadium_management.models import Seat


class Invoice(TimeStampedModel):
    class InvoiceStatus(models.TextChoices):
        PENDING = "PEND", "Pending"
        PAID = "PAID", "Paid"
        CANCELLED = "CANC", "Cancelled"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        choices=InvoiceStatus.choices,
        default=InvoiceStatus.PENDING,
        max_length=4,
        db_index=True,
    )
    total_price = models.PositiveIntegerField(default=0)
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _("invoice")
        verbose_name_plural = _("invoices")

    def __str__(self):
        return f"invoice of {self.user} has status {self.status}"

    def pay(self):
        self.status = Invoice.InvoiceStatus.PAID
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at"])


class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT)
    full_name = models.CharField(max_length=127)
    created_at = models.DateTimeField(default=timezone.now)
    expired = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("invoice_item")
        verbose_name_plural = _("invoice_items")
        constraints = [
            UniqueConstraint(
                fields=["invoice_id", "seat_id"],
                name="seat_can_be_bought_one_time",
            ),
            CheckConstraint(
                check=~Q(full_name=""),
                name="full_name_can_not_be_empty",
            ),
        ]

    def __str__(self):
        return f"item of invoice {self.invoice_id} for seat {self.seat_id}"

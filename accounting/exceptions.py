from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import ValidationError


class AlreadyReservedSeatError(ValidationError):
    """
    It's not possible to reserve seat two time,
    so it will be raised
    """

    code = "already_reserved_seat"
    detail = "Already reserved seat"


class OnlyInvoiceOwner(PermissionDenied):
    """
    Only invoice owner has access to this operation
    So this exception is used to deny user
    """

    code = "only_invoice_owner"
    detail = "You do not have permission to view this invoice"


class OnlyPendingInvoice(PermissionDenied):
    """
    Only invoices in pending status can be modified as others are finalized
    """

    code = "only_pending_invoice"
    detail = "Only pending invoices can be modified!"

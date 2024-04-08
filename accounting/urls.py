from django.urls import path

from accounting.views import AddInvoiceItemView
from accounting.views import InvoiceView
from accounting.views import PayInvoiceView
from accounting.views import RemoveItemFromInvoiceView

app_name = "accounting"

urlpatterns = [
    path("invoice/<int:invoice_id>/", InvoiceView.as_view(), name="invoice"),
    path("invoice/item/add/", AddInvoiceItemView.as_view(), name="add-invoice-item"),
    path(
        "invoice/item/<int:item_id>/remove/",
        RemoveItemFromInvoiceView.as_view(),
        name="remove-invoice-item",
    ),
    path("invoice/pay/<int:invoice_id>/", PayInvoiceView.as_view(), name="pay-invoice"),
]

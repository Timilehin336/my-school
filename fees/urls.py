from django.urls import path
from . import views

urlpatterns = [
    path("", views.invoice_list, name="invoice_list"),
    path("<int:pk>/", views.invoice_detail, name="invoice_detail"),
    path("<int:invoice_id>/pay/", views.record_payment, name="record_payment"),
]

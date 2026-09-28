from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Invoice, Payment


@login_required
def invoice_list(request):
    user = request.user
    if user.is_admin_role:
        invoices = Invoice.objects.select_related("student__user", "category")
    elif user.is_student_role:
        invoices = Invoice.objects.filter(student=getattr(user, "student_profile", None))
    else:
        invoices = Invoice.objects.none()
    return render(request, "fees/invoice_list.html", {"invoices": invoices})


@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.user.is_student_role and request.user.student_profile.pk != invoice.student_id:
        messages.error(request, "You can only view your own invoices.")
        return redirect("dashboard")
    return render(request, "fees/invoice_detail.html", {"invoice": invoice})


@login_required
@user_passes_test(lambda u: u.is_admin_role)
def record_payment(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    if request.method == "POST":
        amount = request.POST.get("amount")
        method = request.POST.get("method", "cash")
        reference = request.POST.get("reference", "")
        if amount:
            Payment.objects.create(invoice=invoice, amount=amount, method=method, reference=reference)
            messages.success(request, "Payment recorded.")
        return redirect("invoice_detail", pk=invoice.pk)
    return redirect("invoice_detail", pk=invoice.pk)

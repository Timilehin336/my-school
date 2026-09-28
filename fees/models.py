from django.db import models
from django.utils import timezone
from students.models import StudentProfile
from academics.models import AcademicYear


class FeeCategory(models.Model):
    name = models.CharField(max_length=100, help_text="e.g. Tuition, Transport, Library")

    def __str__(self):
        return self.name


class Invoice(models.Model):
    class Status(models.TextChoices):
        UNPAID = "unpaid", "Unpaid"
        PARTIAL = "partial", "Partially Paid"
        PAID = "paid", "Paid"
        OVERDUE = "overdue", "Overdue"

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="invoices")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(FeeCategory, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.UNPAID)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-issue_date"]

    def __str__(self):
        return f"Invoice #{self.pk} - {self.student} - {self.amount}"

    @property
    def amount_paid(self):
        return sum(p.amount for p in self.payments.all())

    @property
    def balance(self):
        return float(self.amount) - float(self.amount_paid)

    def refresh_status(self):
        paid = self.amount_paid
        if paid <= 0:
            self.status = self.Status.OVERDUE if self.due_date < timezone.now().date() else self.Status.UNPAID
        elif paid < float(self.amount):
            self.status = self.Status.PARTIAL
        else:
            self.status = self.Status.PAID
        self.save(update_fields=["status"])


class Payment(models.Model):
    METHOD_CHOICES = [
        ("cash", "Cash"), ("bank_transfer", "Bank Transfer"),
        ("card", "Card"), ("online", "Online"),
    ]
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default="cash")
    paid_on = models.DateField(default=timezone.now)
    reference = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["-paid_on"]

    def __str__(self):
        return f"Payment {self.amount} for Invoice #{self.invoice_id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invoice.refresh_status()

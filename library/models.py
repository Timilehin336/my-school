from django.db import models
from django.utils import timezone
from students.models import StudentProfile


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=100, blank=True)
    total_copies = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.title

    @property
    def available_copies(self):
        issued = self.issues.filter(returned_on__isnull=True).count()
        return self.total_copies - issued


class BookIssue(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="issues")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="book_issues")
    issued_on = models.DateField(default=timezone.now)
    due_date = models.DateField()
    returned_on = models.DateField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        ordering = ["-issued_on"]

    def __str__(self):
        return f"{self.book} -> {self.student}"

    @property
    def is_overdue(self):
        return self.returned_on is None and self.due_date < timezone.now().date()

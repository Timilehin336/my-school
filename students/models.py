from django.db import models
from django.conf import settings
from academics.models import SchoolClass, Section, AcademicYear


class StudentProfile(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        TRANSFERRED = "transferred", "Transferred"
        WITHDRAWN = "withdrawn", "Withdrawn"
        GRADUATED = "graduated", "Graduated"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile"
    )
    admission_number = models.CharField(max_length=20, unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10, choices=[("male", "Male"), ("female", "Female"), ("other", "Other")], blank=True
    )
    address = models.TextField(blank=True)

    school_class = models.ForeignKey(SchoolClass, on_delete=models.SET_NULL, null=True, related_name="students")
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True, related_name="students")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.SET_NULL, null=True, blank=True)

    guardian_name = models.CharField(max_length=150, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    guardian_email = models.EmailField(blank=True)
    guardian_relationship = models.CharField(max_length=50, blank=True)

    admission_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["admission_number"]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.admission_number})"

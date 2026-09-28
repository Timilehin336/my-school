from django.db import models
from django.conf import settings
from academics.models import Subject, SchoolClass


class TeacherProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="teacher_profile"
    )
    staff_id = models.CharField(max_length=20, unique=True)
    subjects = models.ManyToManyField(Subject, related_name="teachers", blank=True)
    classes_taught = models.ManyToManyField(SchoolClass, related_name="teachers", blank=True)
    date_joined_school = models.DateField(auto_now_add=True)
    qualification = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        ordering = ["staff_id"]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.staff_id})"

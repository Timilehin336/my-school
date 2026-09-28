from django.db import models
from django.conf import settings
from academics.models import SchoolClass


class Announcement(models.Model):
    AUDIENCE_CHOICES = [
        ("all", "Everyone"), ("teachers", "Teachers Only"),
        ("students", "Students Only"), ("parents", "Parents Only"),
    ]
    title = models.CharField(max_length=200)
    body = models.TextField()
    audience = models.CharField(max_length=10, choices=AUDIENCE_CHOICES, default="all")
    school_class = models.ForeignKey(
        SchoolClass, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Leave blank to send to the whole audience group",
    )
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

from django.db import models
from students.models import StudentProfile
from academics.models import Section


class AttendanceRecord(models.Model):
    class Status(models.TextChoices):
        PRESENT = "present", "Present"
        ABSENT = "absent", "Absent"
        LATE = "late", "Late"
        EXCUSED = "excused", "Excused"

    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="attendance_records")
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)
    marked_by = models.ForeignKey(
        "teachers.TeacherProfile", on_delete=models.SET_NULL, null=True, blank=True
    )
    remarks = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ("student", "date")
        ordering = ["-date"]

    def __str__(self):
        return f"{self.student} - {self.date} - {self.get_status_display()}"

from django.db import models
from academics.models import Section, Subject
from teachers.models import TeacherProfile


class TimetableSlot(models.Model):
    DAY_CHOICES = [
        ("mon", "Monday"), ("tue", "Tuesday"), ("wed", "Wednesday"),
        ("thu", "Thursday"), ("fri", "Friday"), ("sat", "Saturday"),
    ]
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="timetable_slots")
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="timetable_slots")
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.SET_NULL, null=True, related_name="timetable_slots")
    room = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["day", "start_time"]

    def __str__(self):
        return f"{self.section} - {self.get_day_display()} {self.start_time}-{self.end_time} - {self.subject}"

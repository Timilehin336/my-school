from django.db import models
from academics.models import SchoolClass, Subject, AcademicYear
from students.models import StudentProfile


class Exam(models.Model):
    name = models.CharField(max_length=100, help_text="e.g. Mid-Term, Final Exam")
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="exams")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name="exams")
    start_date = models.DateField()
    end_date = models.DateField()
    max_marks_default = models.PositiveIntegerField(default=100)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} - {self.school_class} ({self.academic_year})"


class Mark(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="marks")
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name="marks")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="marks")
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2)
    max_marks = models.PositiveIntegerField(default=100)
    remarks = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ("exam", "student", "subject")

    def __str__(self):
        return f"{self.student} - {self.subject} - {self.marks_obtained}/{self.max_marks}"

    @property
    def percentage(self):
        if self.max_marks:
            return round((float(self.marks_obtained) / self.max_marks) * 100, 1)
        return 0

    @property
    def grade_letter(self):
        pct = self.percentage
        if pct >= 90:
            return "A+"
        if pct >= 80:
            return "A"
        if pct >= 70:
            return "B"
        if pct >= 60:
            return "C"
        if pct >= 50:
            return "D"
        return "F"

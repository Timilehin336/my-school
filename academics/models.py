from django.db import models


class AcademicYear(models.Model):
    name = models.CharField(max_length=20, help_text="e.g. 2026/2027")
    start_date = models.DateField()
    end_date = models.DateField()
    is_current = models.BooleanField(default=False)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.is_current:
            AcademicYear.objects.exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class SchoolClass(models.Model):
    """e.g. Grade 1, Grade 2, JSS 1"""
    name = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0, help_text="Used for sorting classes")

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Section(models.Model):
    """e.g. Grade 1 - A"""
    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="sections")
    name = models.CharField(max_length=10, help_text="e.g. A, B, Blue")
    class_teacher = models.ForeignKey(
        "teachers.TeacherProfile", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="sections_managed",
    )

    class Meta:
        ordering = ["school_class__order", "name"]
        unique_together = ("school_class", "name")

    def __str__(self):
        return f"{self.school_class.name} - {self.name}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    classes = models.ManyToManyField(SchoolClass, related_name="subjects", blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"

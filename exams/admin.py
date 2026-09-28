from django.contrib import admin
from .models import Exam, Mark


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "school_class", "academic_year", "start_date", "end_date")
    list_filter = ("school_class", "academic_year")


@admin.register(Mark)
class MarkAdmin(admin.ModelAdmin):
    list_display = ("exam", "student", "subject", "marks_obtained", "max_marks")
    list_filter = ("exam", "subject")
    search_fields = ("student__admission_number",)

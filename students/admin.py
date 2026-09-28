from django.contrib import admin
from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ("admission_number", "user", "school_class", "section", "status")
    list_filter = ("school_class", "section", "status")
    search_fields = ("admission_number", "user__first_name", "user__last_name")

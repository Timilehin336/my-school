from django.contrib import admin
from .models import TeacherProfile


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ("staff_id", "user", "qualification")
    filter_horizontal = ("subjects", "classes_taught")
    search_fields = ("staff_id", "user__first_name", "user__last_name")

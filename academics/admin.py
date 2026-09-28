from django.contrib import admin
from .models import AcademicYear, SchoolClass, Section, Subject


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    list_display = ("name", "start_date", "end_date", "is_current")
    list_filter = ("is_current",)


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("name", "order")
    ordering = ("order",)


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("school_class", "name", "class_teacher")
    list_filter = ("school_class",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    filter_horizontal = ("classes",)

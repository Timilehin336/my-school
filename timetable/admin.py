from django.contrib import admin
from .models import TimetableSlot


@admin.register(TimetableSlot)
class TimetableSlotAdmin(admin.ModelAdmin):
    list_display = ("section", "day", "start_time", "end_time", "subject", "teacher", "room")
    list_filter = ("section", "day")

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from academics.models import Section
from .models import TimetableSlot

DAY_ORDER = ["mon", "tue", "wed", "thu", "fri", "sat"]


@login_required
def timetable_view(request, section_id):
    section = get_object_or_404(Section, pk=section_id)
    slots = TimetableSlot.objects.filter(section=section).select_related("subject", "teacher__user")
    by_day = {day: [] for day, _ in TimetableSlot.DAY_CHOICES}
    for slot in slots:
        by_day[slot.day].append(slot)
    return render(
        request, "timetable/timetable_view.html",
        {"section": section, "by_day": by_day, "day_choices": TimetableSlot.DAY_CHOICES},
    )

import datetime
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from academics.models import Section
from students.models import StudentProfile
from .models import AttendanceRecord


def _is_staff_role(user):
    return user.is_authenticated and (user.is_admin_role or user.is_teacher_role)


@login_required
@user_passes_test(_is_staff_role)
def mark_attendance(request, section_id):
    section = get_object_or_404(Section, pk=section_id)
    date_str = request.GET.get("date") or datetime.date.today().isoformat()
    selected_date = datetime.date.fromisoformat(date_str)
    students = StudentProfile.objects.filter(section=section, status="active").select_related("user")

    existing = {
        r.student_id: r
        for r in AttendanceRecord.objects.filter(section=section, date=selected_date)
    }

    if request.method == "POST":
        teacher_profile = getattr(request.user, "teacher_profile", None)
        for student in students:
            status = request.POST.get(f"status_{student.pk}", "present")
            record, _created = AttendanceRecord.objects.update_or_create(
                student=student, date=selected_date,
                defaults={"section": section, "status": status, "marked_by": teacher_profile},
            )
        messages.success(request, f"Attendance saved for {section} on {selected_date}.")
        return redirect(f"/attendance/mark/{section.pk}/?date={selected_date}")

    rows = [(student, existing.get(student.pk)) for student in students]
    return render(
        request, "attendance/mark_attendance.html",
        {"section": section, "rows": rows, "selected_date": selected_date, "statuses": AttendanceRecord.Status.choices},
    )


@login_required
@user_passes_test(_is_staff_role)
def attendance_report(request, section_id):
    section = get_object_or_404(Section, pk=section_id)
    records = AttendanceRecord.objects.filter(section=section).select_related("student__user").order_by("-date")
    return render(request, "attendance/attendance_report.html", {"section": section, "records": records[:200]})


@login_required
def my_attendance(request):
    profile = getattr(request.user, "student_profile", None)
    records = AttendanceRecord.objects.filter(student=profile).order_by("-date") if profile else []
    return render(request, "attendance/my_attendance.html", {"records": records})

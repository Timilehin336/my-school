from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Exam, Mark
from students.models import StudentProfile
from academics.models import Subject


def _is_staff_role(user):
    return user.is_authenticated and (user.is_admin_role or user.is_teacher_role)


@login_required
@user_passes_test(_is_staff_role)
def exam_list(request):
    exams = Exam.objects.select_related("school_class", "academic_year")
    return render(request, "exams/exam_list.html", {"exams": exams})


@login_required
@user_passes_test(_is_staff_role)
def enter_marks(request, exam_id, subject_id):
    exam = get_object_or_404(Exam, pk=exam_id)
    subject = get_object_or_404(Subject, pk=subject_id)
    students = StudentProfile.objects.filter(school_class=exam.school_class, status="active").select_related("user")
    existing = {m.student_id: m for m in Mark.objects.filter(exam=exam, subject=subject)}

    if request.method == "POST":
        for student in students:
            raw = request.POST.get(f"marks_{student.pk}", "").strip()
            if raw == "":
                continue
            try:
                marks_value = float(raw)
            except ValueError:
                continue
            Mark.objects.update_or_create(
                exam=exam, student=student, subject=subject,
                defaults={"marks_obtained": marks_value, "max_marks": exam.max_marks_default},
            )
        messages.success(request, f"Marks saved for {subject} - {exam}.")
        return redirect("enter_marks", exam_id=exam.pk, subject_id=subject.pk)

    rows = [(student, existing.get(student.pk)) for student in students]
    return render(
        request, "exams/enter_marks.html",
        {"exam": exam, "subject": subject, "rows": rows},
    )


@login_required
def report_card(request, student_id, exam_id):
    student = get_object_or_404(StudentProfile, pk=student_id)
    exam = get_object_or_404(Exam, pk=exam_id)
    if request.user.is_student_role and request.user.student_profile.pk != student.pk:
        messages.error(request, "You can only view your own report card.")
        return redirect("dashboard")
    marks = Mark.objects.filter(student=student, exam=exam).select_related("subject")
    total_obtained = sum(float(m.marks_obtained) for m in marks)
    total_max = sum(m.max_marks for m in marks)
    overall_pct = round((total_obtained / total_max) * 100, 1) if total_max else 0
    return render(
        request, "exams/report_card.html",
        {"student": student, "exam": exam, "marks": marks, "overall_pct": overall_pct},
    )

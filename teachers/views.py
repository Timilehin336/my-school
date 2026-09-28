from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404
from .models import TeacherProfile


@login_required
@user_passes_test(lambda u: u.is_admin_role)
def teacher_list(request):
    teachers = TeacherProfile.objects.select_related("user").prefetch_related("subjects", "classes_taught")
    return render(request, "teachers/teacher_list.html", {"teachers": teachers})


@login_required
def teacher_detail(request, pk):
    teacher = get_object_or_404(TeacherProfile, pk=pk)
    return render(request, "teachers/teacher_detail.html", {"teacher": teacher})

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from .models import StudentProfile
from .forms import StudentUserForm, StudentProfileForm

User = get_user_model()


def _is_staff_role(user):
    return user.is_authenticated and (user.is_admin_role or user.is_teacher_role)


@login_required
@user_passes_test(_is_staff_role)
def student_list(request):
    query = request.GET.get("q", "")
    students = StudentProfile.objects.select_related("user", "school_class", "section")
    if query:
        students = students.filter(
            Q(user__first_name__icontains=query)
            | Q(user__last_name__icontains=query)
            | Q(admission_number__icontains=query)
        )
    return render(request, "students/student_list.html", {"students": students, "query": query})


@login_required
def student_detail(request, pk):
    profile = get_object_or_404(StudentProfile, pk=pk)
    if request.user.is_student_role and request.user.student_profile.pk != profile.pk:
        messages.error(request, "You can only view your own profile.")
        return redirect("dashboard")
    return render(request, "students/student_detail.html", {"student": profile})


@login_required
@user_passes_test(lambda u: u.is_admin_role)
def student_create(request):
    user_form = StudentUserForm(request.POST or None)
    profile_form = StudentProfileForm(request.POST or None)
    if request.method == "POST" and user_form.is_valid() and profile_form.is_valid():
        user = user_form.save(commit=False)
        user.role = User.Role.STUDENT
        user.set_password("changeme123")
        user.save()
        profile = profile_form.save(commit=False)
        profile.user = user
        profile.save()
        messages.success(request, f"Student {user.get_full_name()} admitted. Default password: changeme123")
        return redirect("student_detail", pk=profile.pk)
    return render(
        request, "students/student_form.html",
        {"user_form": user_form, "profile_form": profile_form, "title": "Admit New Student"},
    )


@login_required
@user_passes_test(lambda u: u.is_admin_role)
def student_edit(request, pk):
    profile = get_object_or_404(StudentProfile, pk=pk)
    user_form = StudentUserForm(request.POST or None, instance=profile.user)
    profile_form = StudentProfileForm(request.POST or None, instance=profile)
    if request.method == "POST" and user_form.is_valid() and profile_form.is_valid():
        user_form.save()
        profile_form.save()
        messages.success(request, "Student record updated.")
        return redirect("student_detail", pk=profile.pk)
    return render(
        request, "students/student_form.html",
        {"user_form": user_form, "profile_form": profile_form, "title": f"Edit {profile.user.get_full_name()}"},
    )

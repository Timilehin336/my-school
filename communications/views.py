from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Announcement


@login_required
def announcement_list(request):
    announcements = Announcement.objects.order_by("-created_at")
    return render(request, "communications/announcement_list.html", {"announcements": announcements})


@login_required
@user_passes_test(lambda u: u.is_admin_role or u.is_teacher_role)
def announcement_create(request):
    if request.method == "POST":
        Announcement.objects.create(
            title=request.POST.get("title", ""),
            body=request.POST.get("body", ""),
            audience=request.POST.get("audience", "all"),
            created_by=request.user,
        )
        messages.success(request, "Announcement posted.")
        return redirect("announcement_list")
    return render(request, "communications/announcement_form.html")

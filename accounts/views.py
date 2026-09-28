import datetime

from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core import signing
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from attendance.models import AttendanceRecord
from communications.models import Announcement
from exams.models import Mark
from fees.models import Invoice
from students.models import StudentProfile
from teachers.models import TeacherProfile

from . import services
from .forms import SignUpForm
from .models import SignupRequest

User = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect("dashboard")

        # Give a helpful message to people whose signup hasn't been approved yet.
        candidate = User.objects.filter(username=request.POST.get("username", "")).first()
        if candidate and not candidate.is_active and candidate.check_password(request.POST.get("password", "")):
            signup = getattr(candidate, "signup_request", None)
            if signup and signup.status == SignupRequest.Status.PENDING:
                notice = "Your account is still waiting for approval. You'll get an email once it's approved."
            elif signup and signup.status == SignupRequest.Status.REJECTED:
                notice = "Your signup request was not approved. Please contact the school office."
            else:
                notice = "This account is inactive. Please contact the school office."
            return render(
                request, "registration/login.html",
                {"form": AuthenticationForm(request), "notice": notice},
            )
    return render(request, "registration/login.html", {"form": form})


def signup_view(request):
    """Public signup. The account is created inactive and emailed to the admin for approval."""
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        data = form.cleaned_data
        with transaction.atomic():
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password=data["password1"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                phone=data.get("phone", ""),
                role=data["role"],
                is_active=False,
            )
            signup_request = SignupRequest.objects.create(user=user, details=form.role_details())
        services.send_approval_email(request, signup_request)
        return render(request, "registration/signup_pending.html", {"applicant": user})

    return render(request, "registration/signup.html", {"form": form})


def approve_signup_view(request, token):
    """Opened from the link in the admin's email. Shows the applicant with Approve / Reject buttons."""
    try:
        pk = services.read_token(token)
    except signing.SignatureExpired:
        return render(request, "registration/approve_signup.html", {"problem": "This approval link has expired. You can still approve the request from the Admin Panel."})
    except signing.BadSignature:
        return render(request, "registration/approve_signup.html", {"problem": "This approval link isn't valid."})

    signup = get_object_or_404(SignupRequest.objects.select_related("user"), pk=pk)
    outcome = None

    if request.method == "POST" and signup.status == SignupRequest.Status.PENDING:
        decision = request.POST.get("decision")
        if decision == "approve":
            services.approve(signup)
            outcome = "approved"
        elif decision == "reject":
            services.reject(signup)
            outcome = "rejected"
        signup.refresh_from_db()

    return render(
        request, "registration/approve_signup.html",
        {"signup": signup, "rows": services.describe_request(signup), "outcome": outcome},
    )


@login_required
def logout_view(request):
    auth_logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


@login_required
def dashboard_view(request):
    user = request.user
    announcements = Announcement.objects.order_by("-created_at")[:5]

    if user.is_admin_role:
        context = {
            "announcements": announcements,
            "total_students": StudentProfile.objects.count(),
            "total_teachers": TeacherProfile.objects.count(),
            "fees_collected": Invoice.objects.aggregate(
                total=Sum("payments__amount")
            )["total"] or 0,
            "fees_due": sum(inv.balance for inv in Invoice.objects.all()),
            "attendance_today": AttendanceRecord.objects.filter(
                date=datetime.date.today(), status="present"
            ).count(),
            "pending_signups": SignupRequest.objects.filter(status=SignupRequest.Status.PENDING).count(),
        }
        return render(request, "accounts/admin_dashboard.html", context)

    if user.is_teacher_role:
        profile = getattr(user, "teacher_profile", None)
        classes = profile.classes_taught.all() if profile else []
        context = {"announcements": announcements, "profile": profile, "classes": classes}
        return render(request, "accounts/teacher_dashboard.html", context)

    if user.is_student_role:
        profile = getattr(user, "student_profile", None)
        marks = Mark.objects.filter(student=profile).select_related("exam", "subject")[:10] if profile else []
        invoices = Invoice.objects.filter(student=profile).order_by("-issue_date")[:5] if profile else []
        attendance_pct = None
        if profile:
            records = AttendanceRecord.objects.filter(student=profile)
            total = records.count()
            present = records.filter(status="present").count()
            attendance_pct = round((present / total) * 100, 1) if total else None
        context = {
            "announcements": announcements,
            "profile": profile,
            "marks": marks,
            "invoices": invoices,
            "attendance_pct": attendance_pct,
        }
        return render(request, "accounts/student_dashboard.html", context)

    if user.is_parent_role:
        children = StudentProfile.objects.filter(guardian_email=user.email)
        context = {"announcements": announcements, "children": children}
        return render(request, "accounts/parent_dashboard.html", context)

    return render(request, "accounts/admin_dashboard.html", {"announcements": announcements})

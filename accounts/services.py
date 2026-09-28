import datetime
import logging

from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from academics.models import AcademicYear, SchoolClass
from students.models import StudentProfile
from teachers.models import TeacherProfile
from .models import User, SignupRequest

logger = logging.getLogger(__name__)

TOKEN_SALT = "signup-approval"
TOKEN_MAX_AGE = 60 * 60 * 24 * 7  # approval links work for 7 days


# ---------- tokens ----------

def make_token(signup_request):
    return signing.dumps(signup_request.pk, salt=TOKEN_SALT)


def read_token(token):
    """Returns the SignupRequest pk. Raises signing.SignatureExpired / BadSignature."""
    return signing.loads(token, salt=TOKEN_SALT, max_age=TOKEN_MAX_AGE)


# ---------- helpers ----------

def _next_code(model, field, prefix, width=4):
    """Next zero-padded code, e.g. prefix 'ADM2026-' -> 'ADM2026-0007'."""
    last = (
        model.objects.filter(**{f"{field}__startswith": prefix})
        .order_by(f"-{field}")
        .first()
    )
    seq = 1
    if last:
        try:
            seq = int(getattr(last, field).split("-")[-1]) + 1
        except ValueError:
            pass
    return f"{prefix}{seq:0{width}d}"


def approval_recipients():
    """Who gets the 'please approve' email."""
    configured = [e.strip() for e in settings.ADMIN_APPROVAL_EMAIL.split(",") if e.strip()]
    if configured:
        return configured
    admins = User.objects.filter(is_active=True, email__gt="").filter(
        Q(role=User.Role.ADMIN) | Q(is_superuser=True)
    )
    return sorted({u.email for u in admins})


def absolute_url(request, path):
    base = getattr(settings, "SITE_URL", "").rstrip("/")
    return f"{base}{path}" if base else request.build_absolute_uri(path)


def describe_request(signup_request):
    """(label, value) rows shown to the admin on the approval page/email."""
    user = signup_request.user
    d = signup_request.details or {}
    rows = [
        ("Name", user.get_full_name()),
        ("Role", user.get_role_display()),
        ("Email", user.email),
        ("Username", user.username),
        ("Phone", user.phone or "—"),
    ]
    if user.role == User.Role.STUDENT:
        cls = SchoolClass.objects.filter(pk=d.get("school_class_id")).first()
        rows += [
            ("Class applying for", str(cls) if cls else "—"),
            ("Date of birth", d.get("date_of_birth") or "—"),
            ("Guardian", d.get("guardian_name") or "—"),
            ("Guardian email", d.get("guardian_email") or "—"),
            ("Guardian phone", d.get("guardian_phone") or "—"),
        ]
    elif user.role == User.Role.TEACHER:
        rows.append(("Qualification", d.get("qualification") or "—"))
    return rows


# ---------- emails ----------

def send_approval_email(request, signup_request):
    """Email the admin(s) a link to review this signup. Returns True if sent."""
    recipients = approval_recipients()
    if not recipients:
        logger.warning("No admin email configured; signup %s needs manual approval.", signup_request.pk)
        return False

    link = absolute_url(
        request, reverse("approve_signup", args=[make_token(signup_request)])
    )
    details = "\n".join(f"  {label}: {value}" for label, value in describe_request(signup_request))
    body = (
        "A new person has asked to join EduManage and is waiting for your approval.\n\n"
        f"{details}\n\n"
        "Review and approve or reject here:\n"
        f"{link}\n\n"
        "This link works for 7 days. Anyone with this email can act on it, so don't forward it.\n"
        "If you don't recognise this person, just reject the request."
    )
    try:
        send_mail(
            subject=f"[EduManage] Approve new {signup_request.user.get_role_display().lower()} signup: "
                    f"{signup_request.user.get_full_name()}",
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipients,
            fail_silently=False,
        )
        return True
    except Exception:
        logger.exception("Could not send approval email for signup %s", signup_request.pk)
        return False


def _notify_applicant(user, subject, body):
    if not user.email:
        return
    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
    except Exception:
        logger.exception("Could not email applicant %s", user.email)


# ---------- decisions ----------

@transaction.atomic
def approve(signup_request):
    """Activate the account and create the role profile. Returns False if already decided."""
    if signup_request.status != SignupRequest.Status.PENDING:
        return False
    user = signup_request.user
    d = signup_request.details or {}

    if user.role == User.Role.STUDENT and not hasattr(user, "student_profile"):
        dob = d.get("date_of_birth")
        StudentProfile.objects.create(
            user=user,
            admission_number=_next_code(StudentProfile, "admission_number", f"ADM{datetime.date.today().year}-"),
            date_of_birth=datetime.date.fromisoformat(dob) if dob else None,
            school_class=SchoolClass.objects.filter(pk=d.get("school_class_id")).first(),
            academic_year=AcademicYear.objects.filter(is_current=True).first(),
            guardian_name=d.get("guardian_name", ""),
            guardian_email=d.get("guardian_email", ""),
            guardian_phone=d.get("guardian_phone", ""),
        )
    elif user.role == User.Role.TEACHER and not hasattr(user, "teacher_profile"):
        TeacherProfile.objects.create(
            user=user,
            staff_id=_next_code(TeacherProfile, "staff_id", "STF-"),
            qualification=d.get("qualification", ""),
            phone=user.phone,
        )

    user.is_active = True
    user.save(update_fields=["is_active"])
    signup_request.status = SignupRequest.Status.APPROVED
    signup_request.decided_at = timezone.now()
    signup_request.save(update_fields=["status", "decided_at"])

    _notify_applicant(
        user,
        "Your EduManage account has been approved",
        f"Hi {user.first_name or user.username},\n\n"
        "Your account has been approved. You can now log in with the username "
        f"'{user.username}' and the password you chose.\n\nWelcome aboard!",
    )
    return True


@transaction.atomic
def reject(signup_request):
    if signup_request.status != SignupRequest.Status.PENDING:
        return False
    signup_request.status = SignupRequest.Status.REJECTED
    signup_request.decided_at = timezone.now()
    signup_request.save(update_fields=["status", "decided_at"])
    user = signup_request.user
    _notify_applicant(
        user,
        "Your EduManage signup request",
        f"Hi {user.first_name or user.username},\n\n"
        "Unfortunately your signup request wasn't approved. "
        "Please contact the school office if you think this is a mistake.",
    )
    return True

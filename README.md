# EduManage — School Management System

A full-stack school management system built with **Django** (backend) and **Tailwind CSS** (frontend, via CDN — no Node/npm build step needed).

## Features

- **Role-based accounts**: Admin, Teacher, Student, Parent — each with their own dashboard
- **Public signup with email approval** — new accounts stay locked until you approve them
- **Student records & admissions** — admit, view, edit, search students
- **Attendance** — mark daily attendance per section, view reports and per-student history
- **Exams & grades** — create exams, enter marks per subject, auto-generated printable report cards
- **Fees & billing** — invoices, payment recording, balance/status tracking
- **Timetable** — per-section weekly schedule
- **Library** — book catalog, issue/return tracking
- **Announcements** — school-wide or audience-targeted notices
- **Custom-themed Django admin panel** for full data management (classes, sections, subjects, timetable slots, fee categories, etc.)

## Requirements

- Python 3.10+
- pip

## Setup

```bash
# 1. Unzip and enter the project
cd school_management_system

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py makemigrations
python manage.py migrate

# 5. (Recommended) Seed demo data — creates an admin, a teacher, two students,
#    a parent, classes, subjects, an exam, an invoice, and an announcement
python manage.py seed_demo_data

# 6. Run the dev server
python manage.py runserver
```

Visit **http://127.0.0.1:8000/** for the app, and **http://127.0.0.1:8000/admin/** for the admin panel.

If you skip step 5, create your own admin account instead:

```bash
python manage.py createsuperuser
```

## Demo logins (after seeding)

| Role    | Username    | Password      |
|---------|-------------|---------------|
| Admin   | `admin`     | `admin12345`  |
| Teacher | `tteacher`  | `teacher12345`|
| Student | `sstudent1` | `student12345`|
| Parent  | `pparent`   | `parent12345` |

**Change these before deploying anywhere public.**

## Project structure

```
school_management/       # Django project settings, urls
accounts/                 # Custom User model (roles), login, signup + approval flow, dashboard router
academics/                 # AcademicYear, SchoolClass, Section, Subject + seed_demo_data command
students/                   # StudentProfile, admission form, list/detail views
teachers/                   # TeacherProfile
attendance/                 # Attendance marking & reports
exams/                      # Exams, marks, report cards
fees/                       # Fee categories, invoices, payments
timetable/                  # Weekly timetable per section
library/                    # Book catalog & issue tracking
communications/             # Announcements
templates/                  # All HTML templates (Tailwind via CDN)
  admin/base_site.html      # Custom-branded admin panel
static/css/admin_custom.css # Admin panel theme
```

## Signup & approval by email

Anyone can request an account at `/accounts/signup/` as a **Student, Teacher or Parent** (Admin accounts can't be created this way). What happens next:

1. The new account is created **inactive** — the person can't log in yet.
2. You get an email with the applicant's details and a secure **Review** link (valid 7 days).
3. Opening the link shows the details with **Approve / Reject** buttons. You don't need to be logged in.
4. On approval the account is activated, their student/teacher profile is created (admission number / staff ID are auto-generated), and they're emailed that they can log in.

You can also handle requests without email: the admin dashboard shows a "waiting for approval" banner, and **Admin Panel → Signup requests** has *Approve/Reject selected* actions.

### Where the emails go

By default emails are **printed in the terminal** running `runserver` (great for testing — copy the link from there). To send real email, set these in Command Prompt **before** `python manage.py runserver` (same window; no quotes):

```bat
set ADMIN_APPROVAL_EMAIL=you@gmail.com
set DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
set EMAIL_HOST_USER=you@gmail.com
set EMAIL_HOST_PASSWORD=your-16-character-app-password
python manage.py runserver
```

- `ADMIN_APPROVAL_EMAIL` is where approval requests are sent (comma-separate several addresses).
- For Gmail you need an **App Password** (Google Account → Security → 2-Step Verification → App passwords); your normal password won't work.
- If you'll approve from another device (e.g. your phone), also `set SITE_URL=http://YOUR-PC-IP:8000` (or your real domain once deployed) so the link in the email is reachable.
- Anyone who has the email can approve the request, so keep that inbox private.

## Day-to-day admin workflow

Most structural setup (classes, sections, subjects, timetable slots, fee categories, assigning teachers to classes/subjects) is done through the **Admin Panel** (`/admin/`), which has been re-themed to match the app. Day-to-day operations (admitting students, marking attendance, entering marks, recording payments, posting announcements) are done through the main app UI.

## Notes & next steps

- **Email/SMS notifications** are not wired up — `Announcement` and attendance alerts are stored in-app only. Add `django.core.mail` (or a provider like SendGrid/Twilio) if you need real notifications.
- **Parent–student linking** is currently done by matching the parent's account email to a student's `guardian_email` field. For production, consider an explicit `ManyToMany` link managed from the admin panel instead.
- **Default student passwords** are set to `changeme123` on admission — swap in a proper "send invite" / password-reset email flow before going live.
- **Static/media files**: `python manage.py collectstatic` before deploying; configure a real media storage backend (e.g. S3) for uploaded profile photos.
- **Production checklist**: set `DJANGO_SECRET_KEY` and `DJANGO_DEBUG=False` as environment variables, set real `ALLOWED_HOSTS`, switch off SQLite in favor of PostgreSQL, and put it behind HTTPS.

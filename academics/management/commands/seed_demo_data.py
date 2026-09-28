import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from academics.models import AcademicYear, SchoolClass, Section, Subject
from teachers.models import TeacherProfile
from students.models import StudentProfile
from fees.models import FeeCategory, Invoice
from exams.models import Exam
from communications.models import Announcement

User = get_user_model()


class Command(BaseCommand):
    help = "Seed the database with demo data (users, classes, students, teachers, etc.)"

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")

        # Superuser / admin
        if not User.objects.filter(username="admin").exists():
            admin = User.objects.create_superuser(
                username="admin", email="admin@edumanage.test", password="admin12345",
                first_name="Ada", last_name="Admin", role=User.Role.ADMIN,
            )
        else:
            admin = User.objects.get(username="admin")

        # Academic year
        year, _ = AcademicYear.objects.get_or_create(
            name="2026/2027",
            defaults={
                "start_date": datetime.date(2026, 9, 1),
                "end_date": datetime.date(2027, 7, 31),
                "is_current": True,
            },
        )

        # Classes & sections
        grade1, _ = SchoolClass.objects.get_or_create(name="Grade 1", order=1)
        grade2, _ = SchoolClass.objects.get_or_create(name="Grade 2", order=2)
        section_1a, _ = Section.objects.get_or_create(school_class=grade1, name="A")
        section_2a, _ = Section.objects.get_or_create(school_class=grade2, name="A")

        # Subjects
        maths, _ = Subject.objects.get_or_create(name="Mathematics", code="MATH")
        english, _ = Subject.objects.get_or_create(name="English", code="ENG")
        science, _ = Subject.objects.get_or_create(name="Science", code="SCI")
        for subj in (maths, english, science):
            subj.classes.add(grade1, grade2)

        # Teacher
        if not User.objects.filter(username="tteacher").exists():
            teacher_user = User.objects.create_user(
                username="tteacher", email="teacher@edumanage.test", password="teacher12345",
                first_name="Tolu", last_name="Teacher", role=User.Role.TEACHER,
            )
            teacher_profile = TeacherProfile.objects.create(
                user=teacher_user, staff_id="STF001", qualification="B.Ed",
            )
            teacher_profile.subjects.add(maths, english, science)
            teacher_profile.classes_taught.add(grade1, grade2)
            section_1a.class_teacher = teacher_profile
            section_1a.save()

        # Students
        demo_students = [
            ("sstudent1", "Sam", "Student", "ADM2026001", section_1a, grade1),
            ("sstudent2", "Sade", "Student", "ADM2026002", section_2a, grade2),
        ]
        for username, first, last, adm_no, section, school_class in demo_students:
            if User.objects.filter(username=username).exists():
                continue
            student_user = User.objects.create_user(
                username=username, email=f"{username}@edumanage.test", password="student12345",
                first_name=first, last_name=last, role=User.Role.STUDENT,
            )
            StudentProfile.objects.create(
                user=student_user, admission_number=adm_no,
                school_class=school_class, section=section, academic_year=year,
                guardian_name="Guardian " + last, guardian_phone="+2348000000000",
                guardian_email=f"parent_{username}@edumanage.test",
                guardian_relationship="Parent",
            )

        # Parent (linked by matching email to a student's guardian_email)
        if not User.objects.filter(username="pparent").exists():
            User.objects.create_user(
                username="pparent", email="parent_sstudent1@edumanage.test", password="parent12345",
                first_name="Pat", last_name="Parent", role=User.Role.PARENT,
            )

        # Fee category + sample invoice
        tuition, _ = FeeCategory.objects.get_or_create(name="Tuition")
        student1 = StudentProfile.objects.filter(admission_number="ADM2026001").first()
        if student1:
            Invoice.objects.get_or_create(
                student=student1, academic_year=year, category=tuition,
                defaults={
                    "amount": 500.00,
                    "due_date": datetime.date(2026, 12, 1),
                },
            )

        # Exam
        Exam.objects.get_or_create(
            name="Mid-Term", school_class=grade1, academic_year=year,
            defaults={
                "start_date": datetime.date(2026, 11, 3),
                "end_date": datetime.date(2026, 11, 10),
                "max_marks_default": 100,
            },
        )

        # Announcement
        Announcement.objects.get_or_create(
            title="Welcome to the new academic year!",
            defaults={
                "body": "We're excited to kick off 2026/2027. Please check your dashboards regularly.",
                "audience": "all",
                "created_by": admin,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully."))
        self.stdout.write(self.style.SUCCESS("Login: admin / admin12345 (Admin panel + app)"))
        self.stdout.write(self.style.SUCCESS("Login: tteacher / teacher12345 (Teacher)"))
        self.stdout.write(self.style.SUCCESS("Login: sstudent1 / student12345 (Student)"))
        self.stdout.write(self.style.SUCCESS("Login: pparent / parent12345 (Parent)"))

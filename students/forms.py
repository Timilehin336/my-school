from django import forms
from django.contrib.auth import get_user_model
from .models import StudentProfile

User = get_user_model()

TAILWIND_INPUT = (
    "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm "
    "focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:outline-none"
)


class StudentUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username"]
        widgets = {f: forms.TextInput(attrs={"class": TAILWIND_INPUT}) for f in fields}
        widgets["email"] = forms.EmailInput(attrs={"class": TAILWIND_INPUT})


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = [
            "admission_number", "date_of_birth", "gender", "address",
            "school_class", "section", "academic_year",
            "guardian_name", "guardian_phone", "guardian_email", "guardian_relationship",
            "status",
        ]
        widgets = {
            "admission_number": forms.TextInput(attrs={"class": TAILWIND_INPUT}),
            "date_of_birth": forms.DateInput(attrs={"class": TAILWIND_INPUT, "type": "date"}),
            "gender": forms.Select(attrs={"class": TAILWIND_INPUT}),
            "address": forms.Textarea(attrs={"class": TAILWIND_INPUT, "rows": 2}),
            "school_class": forms.Select(attrs={"class": TAILWIND_INPUT}),
            "section": forms.Select(attrs={"class": TAILWIND_INPUT}),
            "academic_year": forms.Select(attrs={"class": TAILWIND_INPUT}),
            "guardian_name": forms.TextInput(attrs={"class": TAILWIND_INPUT}),
            "guardian_phone": forms.TextInput(attrs={"class": TAILWIND_INPUT}),
            "guardian_email": forms.EmailInput(attrs={"class": TAILWIND_INPUT}),
            "guardian_relationship": forms.TextInput(attrs={"class": TAILWIND_INPUT}),
            "status": forms.Select(attrs={"class": TAILWIND_INPUT}),
        }

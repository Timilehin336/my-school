from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from academics.models import SchoolClass

User = get_user_model()

TAILWIND_INPUT = (
    "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm "
    "focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 focus:outline-none"
)

# Admin accounts can never be created through public signup.
SIGNUP_ROLES = [
    (User.Role.STUDENT, "Student"),
    (User.Role.TEACHER, "Teacher"),
    (User.Role.PARENT, "Parent"),
]


class SignUpForm(forms.Form):
    role = forms.ChoiceField(
        choices=SIGNUP_ROLES, label="I am signing up as",
        widget=forms.Select(attrs={"class": TAILWIND_INPUT}),
    )
    first_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": TAILWIND_INPUT}))
    last_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": TAILWIND_INPUT}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"class": TAILWIND_INPUT}))
    phone = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={"class": TAILWIND_INPUT}))
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"class": TAILWIND_INPUT}))

    # Student-only (optional)
    school_class = forms.ModelChoiceField(
        queryset=SchoolClass.objects.all(), required=False, label="Class applying for",
        widget=forms.Select(attrs={"class": TAILWIND_INPUT}),
    )
    date_of_birth = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"class": TAILWIND_INPUT, "type": "date"}),
    )
    guardian_name = forms.CharField(
        max_length=150, required=False, label="Parent/Guardian name",
        widget=forms.TextInput(attrs={"class": TAILWIND_INPUT}),
    )
    guardian_email = forms.EmailField(
        required=False, label="Parent/Guardian email",
        widget=forms.EmailInput(attrs={"class": TAILWIND_INPUT}),
    )
    guardian_phone = forms.CharField(
        max_length=20, required=False, label="Parent/Guardian phone",
        widget=forms.TextInput(attrs={"class": TAILWIND_INPUT}),
    )

    # Teacher-only (optional)
    qualification = forms.CharField(
        max_length=200, required=False, widget=forms.TextInput(attrs={"class": TAILWIND_INPUT}),
    )

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={"class": TAILWIND_INPUT}))
    password2 = forms.CharField(label="Confirm password", widget=forms.PasswordInput(attrs={"class": TAILWIND_INPUT}))

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("That username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with that email already exists.")
        return email

    def clean(self):
        cleaned = super().clean()
        p1, p2 = cleaned.get("password1"), cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords don't match.")
        if p1:
            try:
                validate_password(p1)
            except ValidationError as e:
                self.add_error("password1", e)
        return cleaned

    def role_details(self):
        """Role-specific answers, stored on the SignupRequest until approval."""
        data = self.cleaned_data
        role = data["role"]
        if role == User.Role.STUDENT:
            dob = data.get("date_of_birth")
            sc = data.get("school_class")
            return {
                "school_class_id": sc.pk if sc else None,
                "date_of_birth": dob.isoformat() if dob else None,
                "guardian_name": data.get("guardian_name", ""),
                "guardian_email": data.get("guardian_email", ""),
                "guardian_phone": data.get("guardian_phone", ""),
            }
        if role == User.Role.TEACHER:
            return {"qualification": data.get("qualification", "")}
        return {}

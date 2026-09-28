def role_flags(request):
    """Make role-check booleans available in every template without
    repeating `user.role == '...'` everywhere."""
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return {}
    return {
        "is_admin_role": user.role == "admin" or user.is_superuser,
        "is_teacher_role": user.role == "teacher",
        "is_student_role": user.role == "student",
        "is_parent_role": user.role == "parent",
    }

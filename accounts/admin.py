from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin

from . import services
from .models import User, SignupRequest


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "first_name", "last_name", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff", "is_superuser")
    fieldsets = UserAdmin.fieldsets + (
        ("School Role", {"fields": ("role", "phone", "profile_photo")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("School Role", {"fields": ("role", "phone", "email", "first_name", "last_name")}),
    )


@admin.register(SignupRequest)
class SignupRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "status", "created_at", "decided_at")
    list_filter = ("status", "user__role")
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    readonly_fields = ("user", "details", "created_at", "decided_at")
    actions = ["approve_selected", "reject_selected"]

    @admin.display(description="Role")
    def role(self, obj):
        return obj.user.get_role_display()

    @admin.action(description="Approve selected signups")
    def approve_selected(self, request, queryset):
        count = sum(1 for s in queryset.select_related("user") if services.approve(s))
        self.message_user(request, f"{count} signup(s) approved.", messages.SUCCESS)

    @admin.action(description="Reject selected signups")
    def reject_selected(self, request, queryset):
        count = sum(1 for s in queryset.select_related("user") if services.reject(s))
        self.message_user(request, f"{count} signup(s) rejected.", messages.SUCCESS)

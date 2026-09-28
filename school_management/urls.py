from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import dashboard_view

admin.site.site_header = "EduManage Administration"
admin.site.site_title = "EduManage Admin"
admin.site.index_title = "Welcome to the EduManage control panel"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", dashboard_view, name="dashboard"),
    path("accounts/", include("accounts.urls")),
    path("students/", include("students.urls")),
    path("teachers/", include("teachers.urls")),
    path("attendance/", include("attendance.urls")),
    path("exams/", include("exams.urls")),
    path("fees/", include("fees.urls")),
    path("timetable/", include("timetable.urls")),
    path("library/", include("library.urls")),
    path("announcements/", include("communications.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

from django.urls import path
from . import views

urlpatterns = [
    path("mark/<int:section_id>/", views.mark_attendance, name="mark_attendance"),
    path("report/<int:section_id>/", views.attendance_report, name="attendance_report"),
    path("mine/", views.my_attendance, name="my_attendance"),
]

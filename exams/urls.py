from django.urls import path
from . import views

urlpatterns = [
    path("", views.exam_list, name="exam_list"),
    path("<int:exam_id>/subject/<int:subject_id>/marks/", views.enter_marks, name="enter_marks"),
    path("report-card/<int:student_id>/<int:exam_id>/", views.report_card, name="report_card"),
]

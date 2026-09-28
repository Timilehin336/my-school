from django.urls import path
from . import views

urlpatterns = [
    path("<int:section_id>/", views.timetable_view, name="timetable_view"),
]

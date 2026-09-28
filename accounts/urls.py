from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("approve/<str:token>/", views.approve_signup_view, name="approve_signup"),
    path("logout/", views.logout_view, name="logout"),
]

from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("signup/", views.signup_api, name="signup_api"),
    # path("login/", views.login_api, name="login_api"),
    # path("logout/", views.logout_api, name="logout_api"),
    # path("change-password/", views.change_pass_api, name="change_password_api"),
    # path("activate/<uidb64>/<str:token>/", views.activate_api, name="activate_api"),
]
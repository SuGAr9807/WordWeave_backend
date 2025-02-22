from django.urls import path
from django.contrib.auth import views as auth_views

# . means call/import all the things inside the views.py
from . import views

# all the api calls are handled here luike signup then go to views.signup
# if login then call views.login_api function from views

urlpatterns = [
    path("signup/", views.signup_api, name="signup_api"),
    path("login/", views.login_api, name="login_api"),
    path("logout/", views.logout_api, name="logout_api"),
     path("password-reset/", views.request_password_reset, name="password_reset"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path("change-password/", views.change_pass_api, name="change_password_api"),
]
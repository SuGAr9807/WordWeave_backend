from django.urls import path
from django.contrib.auth import views as auth_views

# . means call/import all the things inside the views.py
from . import views

# all the api calls are handled here luike signup then go to views.signup
# if login then call views.login_api function from views

urlpatterns = [
    path("signup/", views.signup_api, name="signup_api"),
    path("login/", views.login_api, name="login_api"),
     path("password-reset/", views.request_password_reset, name="password_reset"),
    path(
        "password-reset-confirm/<uidb64>/<token>/",
        views.password_reset_confirm,
        name="password_reset_confirm",
    ),
    path("me/", views.me_api, name="me_api"),
    path("change-password/", views.change_pass_api, name="change_password_api"), 
    path("blogs-create/", views.blog_list_create, name="blog_create"),
    path("blogs-list/", views.blog_list, name="blog_list"),
    path("blogs-list/get-all-user/", views.get_all_user, name="get_all_user"),
    path("blogs-list/<int:user_id>/user-posts/", views.get_all_blogs_by_user, name="get_all_blogs_by_user"),
    path("blogs-list/top-liked-posts/", views.top_liked_blog_list, name="top_liked_blog_list"),
    path("blogs-list/most-commented-posts/", views.most_commented_blog_list, name="most_commented_blog_list"),
    path("blogs-list/<int:post_id>/", views.blog_detail, name="blog_detail"),
    path("blogs/<int:post_id>/like/", views.like_post, name="like_post"),
    path("blogs/<int:post_id>/comment/", views.comment_post, name="comment_post"),
    path("comments/<int:comment_id>/update/", views.update_comment, name="update_comment"),
    path("comments/<int:comment_id>/delete/", views.delete_comment, name="delete_comment"),
    path("tags/add/", views.add_tag, name="add_tag"),
    path("list-tags/", views.list_tags, name="list_tag"),
]
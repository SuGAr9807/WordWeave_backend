from django.contrib import admin
from .models import User, BlogPost, Tag, Like, Comment

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "email", "username", "is_active", "is_staff")
    search_fields = ("email", "username")
    list_filter = ("is_active", "is_staff")
    ordering = ("user_id",)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("post_id", "title", "user", "created_at")
    search_fields = ("title", "user__email")
    list_filter = ("created_at",)
    ordering = ("-created_at",)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("tag_id", "name")
    search_fields = ("name",)

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ("like_id", "post", "user")
    search_fields = ("post__title", "user__email")

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("comment_id", "post", "user", "created_at")
    search_fields = ("post__title", "user__email", "text")
    list_filter = ("created_at",)

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
import cloudinary
import cloudinary.uploader
from django.conf import settings

#########################   DATABASE OF DJANGO ####################

# also called django models
# used for structuring the table of data where the data is stored
# data is stored in form of table 


#django user creation

class UserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username or None, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, username, password, **extra_fields)


# extra fields for user (extension of above user table)
class User(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    access_token = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    profile_picture = models.URLField(null=True, blank=True)  # Store URL instead of ImageField
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_groups",
        blank=True,
    )

    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions",
        blank=True,
    )
    objects = UserManager()

    # Admin side pe data ka name set karta hai
        
    def __str__(self):
        return self.email

    class Meta:
        db_table = "user"
        managed = True

    def upload_profile_picture(self, file):
        result = cloudinary.uploader.upload(file)
        self.profile_picture = result["secure_url"]
        self.save()


# post model where all the articles/blog are saved
class BlogPost(models.Model):
    post_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="blog_posts")
    title = models.CharField(max_length=255)
    content = models.TextField()
    image_url = models.URLField(null=True, blank=True)
    tags = models.ManyToManyField("Tag", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    def upload_profile_picture(self, file):
        result = cloudinary.uploader.upload(file)
        self.image_url = result["secure_url"]
        self.save()

    class Meta:
        db_table = "blog_post"


# to save all tags like fantasy tag, science fiction tag, etc
class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)  # Added tag_id
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "blog_tag"


# to store all the likes and connect it with the post table
class Like(models.Model):
    like_id = models.AutoField(primary_key=True)  # Added like_id
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="likes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.email} liked {self.post.title}"

    class Meta:
        db_table = "blog_like"
        unique_together = ("post", "user")  # Ensures a user can like a post only once


# to create comment for every user and every post
class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)  # Added comment_id
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} commented on {self.post.title}"

    class Meta:
        db_table = "blog_comment"

class FailedLoginAttempt(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    attempt_count = models.IntegerField(default=0)

    class Meta:
        db_table = "failed_login_attempt"
        managed = True

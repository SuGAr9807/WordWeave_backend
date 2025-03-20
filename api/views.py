from django.contrib.auth import authenticate, login, logout, get_user_model
import re
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.http import JsonResponse
import json
import cloudinary.uploader
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.shortcuts import render
from .models import (
    FailedLoginAttempt,
    Comment,
    Like,
    BlogPost,
    Tag
)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.shortcuts import get_object_or_404

User = get_user_model()

# all the apis and request are handled here after coming from the urls.py

# Password validation using regular expression
def validate_password(password):
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter.")

    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter.")

    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit.")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character.")

    return True


# POST request to create user
@csrf_exempt
@api_view(["POST"])
def signup_api(request):
    if request.method == "POST":
        try:
            data = request.data
            username = data.get("username")
            name = data.get("name")
            email = data.get("email")
            password = data.get("password")
            profile_picture = request.FILES.get("profile_picture")

            if not (username and email and password):
                return JsonResponse(
                    {"error": "All fields (username, email, password) are required."},
                    status=400,
                )

            # Validate the password
            try:
                validate_password(password)
            except ValueError as e:
                return JsonResponse({"error": str(e)}, status=400)

            # Upload profile picture to Cloudinary if provided
            profile_picture_url = None
            if profile_picture:
                upload_result = cloudinary.uploader.upload(profile_picture)
                profile_picture_url = upload_result.get("secure_url")
           
            # Create user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                name=name,
                profile_picture=profile_picture_url,
            )
            user.is_active = True
            user.save()

            return JsonResponse(
                {
                    "success": "User created successfully",
                    "profile_picture": profile_picture_url,
                },
                status=201,
            )

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)

        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return JsonResponse(
                {"error": "Network Error: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    else:
        return JsonResponse({"error": "Method not allowed."}, status=405)

@csrf_exempt
@api_view(["POST"])
def login_api(request):
    if request.method == "POST":
        username = request.data.get("email")
        password = request.data.get("password")

        # Authenticate the user
        user = authenticate(username=username, password=password)
        if user is not None:
            # Reset failed login attempts on successful login
            FailedLoginAttempt.objects.filter(user=user).delete()
            login(request, user)

            # Check if the existing token is valid
            if user.access_token:
                try:
                    # Decode the token to check its validity
                    access_token = AccessToken(user.access_token)
                    if access_token["exp"] > datetime.now().timestamp():
                        return Response(
                            {
                                "success": "Login successful.",
                                "access_token": user.access_token,
                            }
                        )
                except Exception as e:
                    # Token is invalid, so generate a new one
                    pass

            # If token is not valid or not present, generate a new one
            try:
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token

                # Save the access token to the user's record
                user.access_token = str(access_token)
                user.save()

                return Response(
                    {
                        "success": "Login successful.",
                        "access_token": str(access_token),
                    }
                )
            except Exception as e:
                return Response(
                    {"error": "Error generating token: " + str(e)},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        else:
            # Handle failed login attempts
            user = User.objects.filter(email=username).first()
            if user:
                failed_attempt, created = FailedLoginAttempt.objects.get_or_create(
                    user=user
                )
                failed_attempt.attempt_count += 1
                failed_attempt.timestamp = timezone.now()
                failed_attempt.save()

                if failed_attempt.attempt_count >= 5:
                    send_password_reset_email(request, user)
                    return Response(
                        {
                            "error": "Too many failed login attempts. Password reset email has been sent."
                        },
                        status=status.HTTP_403_FORBIDDEN,
                    )

            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    else:
        return Response(
            {"error": "Method not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_api(request):
    user = request.user
    user_data = {
        "id": user.user_id,
        "username": user.username,
        "email": user.email,
        "name": user.name,
        "profile_picture": user.profile_picture,
        "is_active": user.is_active,
        "date_joined": user.date_joined,
    }
    return Response(user_data, status=status.HTTP_200_OK)


def send_password_reset_email(request, user):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    mail_subject = "Password Reset Request"
    message = render_to_string(
        "password_reset_email.html",
        {
            "user": user,
            "domain": get_current_site(request).domain,
            "uid": uid,
            "token": token,
        },
    )
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()
    
@api_view(["POST"])
def logout_api(request):
    try:
        logout(request)
        return Response({"success": "Logout successful."}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"error": "Network Error"}, status=status.HTTP_400_BAD_REQUEST)




@api_view(["POST"])
def change_pass_api(request):
    try:
        user = request.user
        data = request.data

        # Retrieve passwords from the request data
        current_password = data.get("current_password")
        new_password = data.get("new_password")

        # Check if the current password is provided
        if not current_password:
            return Response(
                {"error": "Current password is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Authenticate the user with the current password
        if not user.check_password(current_password):
            return Response(
                {"error": "Current password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if the new password is provided
        if not new_password:
            return Response(
                {"error": "New password is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate the new password
        try:
            validate_password(new_password)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Set the new password
        user.set_password(new_password)
        user.save()

        return Response(
            {"success": "Password has been changed successfully."},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        return Response(
            {"error": "An error occurred: " + str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )



@api_view(["GET", "POST"])
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if request.method == "GET":
        if user is not None and default_token_generator.check_token(user, token):
            # Render the password reset form
            return render(
                request,
                "password_reset_confirm.html",
                {"uidb64": uidb64, "token": token},
            )
        else:
            # Invalid token or user not found
            return Response(
                {"error": "Inavalid token or Expired Token"},
                status=status.HTTP_404_NOT_FOUND,
            )

    elif request.method == "POST":
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            new_password = request.data.get("new_password")

            if new_password:
                try:
                    validate_password(new_password)
                except ValueError as e:
                    return JsonResponse({"error": str(e)}, status=400)

                user.set_password(new_password)
                user.save()
                return JsonResponse(
                    {"message": "Password reset successfully."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "invalid Token"}, status=status.HTTP_400_BAD_REQUEST
                )
                
@api_view(["POST"])
def request_password_reset(request):
    data = request.data
    email = data.get("email")

    if not email:
        return Response(
            {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    users = User.objects.filter(Q(email=email))
    if not users.exists():
        return Response(
            {"error": "No user found with this email."},
            status=status.HTTP_404_NOT_FOUND,
        )

    for user in users:
        send_password_reset_email(request, user)

    return Response(
        {"success": "Password reset email has been sent."}, status=status.HTTP_200_OK
    )



@api_view(["GET", "POST"])
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if request.method == "GET":
        if user is not None and default_token_generator.check_token(user, token):
            # Render the password reset form
            return render(
                request,
                "password_reset_confirm.html",
                {"uidb64": uidb64, "token": token},
            )
        else:
            # Invalid token or user not found
            return Response(
                {"error": "Inavalid token or Expired Token"},
                status=status.HTTP_404_NOT_FOUND,
            )

    elif request.method == "POST":
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            new_password = request.data.get("new_password")

            if new_password:
                try:
                    validate_password(new_password)
                except ValueError as e:
                    return JsonResponse({"error": str(e)}, status=400)

                user.set_password(new_password)
                user.save()
                return JsonResponse(
                    {"message": "Password reset successfully."},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "invalid Token"}, status=status.HTTP_400_BAD_REQUEST
                )


# Blog apis
@api_view(["GET"])
def list_tags(request):
    tags = Tag.objects.all().order_by('name')
    data = [
        {
            "tag_id": tag.tag_id,
            "name": tag.name
        }
        for tag in tags
    ]
    return Response(data, status=status.HTTP_200_OK)

@api_view(["POST"])
@permission_classes([IsAdminUser])
def add_tag(request):
    name = request.data.get("name")
    if not name:
        return Response({"error": "Tag name is required."}, status=400)

    tag, created = Tag.objects.get_or_create(name=name)
    return Response({"message": "Tag created!", "tag_id": tag.tag_id}, status=201)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import cloudinary.uploader
from .models import BlogPost, Tag

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def blog_list_create(request):
    if request.method == "POST":
        try:
            data = request.data
            title = data.get("title")
            content = data.get("content")
            tag_ids = data.get("tags", [])
            image = request.FILES.get("image_url")  # Uploaded image file

            if not title or not content:
                return Response(
                    {"error": "Title and content are required."}, 
                    status=400
                )

            # Upload image to Cloudinary if provided
            image_url = None
            if image:
                try:
                    upload_result = cloudinary.uploader.upload(image)
                    image_url = upload_result.get("secure_url")
                except Exception as e:
                    return Response(
                        {"error": f"Image upload failed: {str(e)}"}, 
                        status=500
                    )

            # Create BlogPost
            blog = BlogPost.objects.create(
                user=request.user,
                title=title,
                content=content,
                image_url=image_url  # Store Cloudinary image URL
            )

            # Attach selected tags
            tags = Tag.objects.filter(tag_id__in=tag_ids)
            blog.tags.set(tags)

            return Response(
                {
                    "message": "Blog created successfully!",
                    "post_id": blog.post_id,
                    "image_url": image_url,  # Return uploaded image URL
                },
                status=201,
            )

        except Exception as e:
            return Response(
                {"error": f"Unexpected error: {str(e)}"},
                status=500
            )

    return Response(
        {"error": "Method not allowed."},
        status=405
    )
    
from django.db.models import Count

@api_view(["GET"])
def blog_list(request):
    tag_id = request.GET.get("tag_id")

    # Filter by tag if tag_id is provided
    blogs = BlogPost.objects.all().order_by("-created_at")
    if tag_id:
        blogs = blogs.filter(tags__tag_id=tag_id)

    # Optimize data retrieval using `annotate` to avoid extra queries
    blogs = blogs.annotate(
        likes_count=Count("likes"),
        comments_count=Count("comments")
    ).prefetch_related("tags", "user")

    data = [
        {
            "post_id": blog.post_id,
            "title": blog.title,
            "content": blog.content,
            "user": blog.user.email,
            "tags": list(blog.tags.values_list("name", flat=True)),  # Optimized way to get tag names
            "likes": blog.likes_count,
            "comments": blog.comments_count,
            "created_at": blog.created_at,
            "image_url": blog.image_url,
        }
        for blog in blogs
    ]

    return Response(data, status=status.HTTP_200_OK)
    

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def like_post(request, post_id):
    blog = get_object_or_404(BlogPost, post_id=post_id)
    like, created = Like.objects.get_or_create(post=blog, user=request.user)

    if not created:
        like.delete()
        return Response({"message": "Like removed!"}, status=200)

    return Response({"message": "Post liked!"}, status=200)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def comment_post(request, post_id):
    blog = get_object_or_404(BlogPost, post_id=post_id)
    text = request.data.get("text")

    if not text:
        return Response({"error": "Comment text is required."}, status=400)

    comment = Comment.objects.create(post=blog, user=request.user, text=text)
    return Response({"message": "Comment added!", "comment_id": comment.comment_id}, status=201)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_comment(request, comment_id):
    comment = get_object_or_404(Comment, comment_id=comment_id)

    if request.user != comment.user:
        return Response({"error": "You can only edit your own comments."}, status=403)

    comment.text = request.data.get("text", comment.text)
    comment.save()
    return Response({"message": "Comment updated!"}, status=200)

@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, comment_id=comment_id)

    if request.user != comment.user:
        return Response({"error": "You can only delete your own comments."}, status=403)

    comment.delete()
    return Response({"message": "Comment deleted!"}, status=200)

@api_view(["GET"])
def blog_detail(request, post_id):
    blog = get_object_or_404(BlogPost, post_id=post_id)
    data = {
        "post_id": blog.post_id,
        "title": blog.title,
        "content": blog.content,
        "user": blog.user.email,
        "username": blog.user.username,
        "tags": [tag.name for tag in blog.tags.all()],
        "likes": blog.likes.count(),
        "likes":[
                    {"user": like.user.email,"username":like.user.username}
                    for like in blog.likes.all()
                ],
        "commentCount": blog.comments.count(),
        "comments": [
                    {"comment_id":comment.comment_id,"user": comment.user.email,"username":comment.user.username, "text": comment.text}
                    for comment in blog.comments.all()
                ],
        "created_at": blog.created_at,
    }
    return Response(data, status=status.HTTP_200_OK)


@api_view(["GET"])
def top_liked_blog_list(request):
    # Fetch top 10 most liked blogs, optimized with annotation
    blogs = (
        BlogPost.objects.annotate(
            likes_count=Count("likes"),
            comments_count=Count("comments")
        )
        .prefetch_related("tags", "user")
        .order_by("-likes_count")[:10]  # Sort by most likes and limit to 10
    )

    data = [
        {
            "post_id": blog.post_id,
            "title": blog.title,
            "content": blog.content,
            "user": blog.user.email,
            "tags": list(blog.tags.values_list("name", flat=True)),
            "likes": blog.likes_count,
            "comments": blog.comments_count,
            "created_at": blog.created_at,
            "image_url": blog.image_url,
        }
        for blog in blogs
    ]

    return Response(data, status=status.HTTP_200_OK)
   

@api_view(["GET"])
def most_commented_blog_list(request):
    blogs = (
        BlogPost.objects.annotate(
            likes_count=Count("likes"),
            comments_count=Count("comments")
        )
        .prefetch_related("tags", "user")
        .order_by("-comments_count")[:10]  # Sort by most comments and limit to 10
    )

    data = [
        {
            "post_id": blog.post_id,
            "title": blog.title,
            "content": blog.content,
            "user": blog.user.email,
            "tags": list(blog.tags.values_list("name", flat=True)),
            "likes": blog.likes_count,
            "comments": blog.comments_count,
            "created_at": blog.created_at,
            "image_url": blog.image_url,
        }
        for blog in blogs
    ]

    return Response(data, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_all_user(request):
    # Get all users with annotation for total likes and post count
    users = User.objects.annotate(
        total_likes=Count('blog_posts__likes'),
        posts_count=Count('blog_posts')
    ).order_by('-total_likes')
    
    # Create response data with user information, like count, and post count
    data = [
        {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "name": user.name,
            "profile_picture": user.profile_picture,
            "total_likes": user.total_likes,
            "posts_count": user.posts_count,
            "date_joined": user.date_joined
        }
        for user in users
    ]
    
    return Response(data, status=status.HTTP_200_OK)

@api_view(["GET"])
def get_all_blogs_by_user(request,user_id):
    if not user_id:
        return Response(
            {"error": "User ID is required."}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get the user or return 404 if not found
    user = get_object_or_404(User, user_id=user_id)
    
    # Fetch all blogs by this user with optimized queries
    blogs = (
        BlogPost.objects.filter(user=user)
        .annotate(
            likes_count=Count("likes"),
            comments_count=Count("comments")
        )
        .prefetch_related("tags")
        .order_by("-created_at")
    )
    
    # Format the response data
    data = [
        {
            "post_id": blog.post_id,
            "title": blog.title,
            "content": blog.content,
            "user": user.email,
            "username": user.username,
            "tags": list(blog.tags.values_list("name", flat=True)),
            "likes": blog.likes_count,
            "comments": blog.comments_count,
            "created_at": blog.created_at,
            "image_url": blog.image_url,
        }
        for blog in blogs
    ]
    
    return Response(data, status=status.HTTP_200_OK)
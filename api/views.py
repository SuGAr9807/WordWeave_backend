from django.contrib.auth import authenticate, login, logout, get_user_model
import re
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.http import JsonResponse
import json
import cloudinary.uploader
from rest_framework import status

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

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.http import HttpResponse


class TokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get("Authorization")

        admin_paths = [
            "/admin",
            "/login/",
            "/signup/",
            "/delete-user/",
            "/token/",
            "/password-reset/",
            "/password-reset-confirm/",
            "/"
        ]
        if any(request.path.startswith(path) for path in admin_paths):
            return self.get_response(request)
        if token:
            if not token.startswith("Bearer "):
                return self.invalid_token_response(request)

            token = token.split("Bearer ")[1].strip()

            try:
                JWT_authenticator = JWTAuthentication()
                response = JWT_authenticator.authenticate(request)
                if response:
                    UserData, token = response
                    request.UserData = UserData
                    request.token = token
                    return self.get_response(request)
                else:
                    return self.invalid_token_response(request)
            except InvalidToken:
                return self.invalid_token_response(request)
        else:
            return self.unauthorized_response(request)

    def invalid_token_response(self, request):
        return HttpResponse(
            status=401, content="Invalid token", content_type="text/plain"
        )

    def unauthorized_response(self, request):
        return HttpResponse(
            status=401,
            content="Unauthorized: Token is missing",
            content_type="text/plain",
        )
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

IN_PRODUCTION = settings.IN_PRODUCTION

@csrf_exempt
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid credentials"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Generate tokens
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    response = Response({"message": "Login successful"})

    # Set cookies
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True if IN_PRODUCTION == True else False,
        samesite="None" if IN_PRODUCTION == True else "Lax",
        max_age=60 * 15
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True if IN_PRODUCTION == True else False,
        samesite="None" if IN_PRODUCTION == True else "Lax",
        max_age=60 * 60 * 24
    )

    return response

def refresh_view(request):
    refresh_token = request.COOKIES.get("refresh_token")

    if refresh_token is None:
        return Response({"error": "No refresh token"}, status=401)

    try:
        refresh = RefreshToken(refresh_token)
        access_token = str(refresh.access_token)

        response = Response({"message": "Token refreshed"})

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True if IN_PRODUCTION == True else False,
            samesite="None" if IN_PRODUCTION == True else "Lax",
            max_age=60 * 15
        )

        return response

    except TokenError:
        return Response({"error": "Invalid refresh token"}, status=401)

def logout_view(request):
    response = Response({"message": "Logged out"})

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return response

def auth_status(request):
    if request.user.is_authenticated:
        return JsonResponse({"loggedIn": True, "username": request.user.username})
    return JsonResponse({"loggedIn": False})
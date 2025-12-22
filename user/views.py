from django.contrib.auth import get_user_model
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    UserPublicSerializer,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Auth"],
        summary="Register a new user",
        description="Creates a user and returns JWT access/refresh tokens.",
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                response=None,
                description="User created. Returns user data + JWT tokens."
            ),
            400: OpenApiResponse(description="Validation error"),
        },
        examples=[
            OpenApiExample(
                "Register request",
                value={
                    "email": "user@example.com",
                    "phone_number": "+98123456789",
                    "password": "StrongPass123!",
                    "password2": "StrongPass123!",
                },
                request_only=True,
            ),
            OpenApiExample(
                "Register response",
                value={
                    "user": {
                        "id": 1,
                        "email": "user@example.com",
                        "phone_number": "+98123456789",
                        "date_joined": "2025-12-22T10:15:30Z",
                    },
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9....",
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9....",
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        data = {
            "user": UserPublicSerializer(user).data,
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_201_CREATED)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

    @extend_schema(
        tags=["Auth"],
        summary="Login (JWT)",
        description="Returns JWT access/refresh tokens. Uses email + password.",
        examples=[
            OpenApiExample(
                "Login request",
                value={"email": "user@example.com", "password": "StrongPass123!"},
                request_only=True,
            ),
            OpenApiExample(
                "Login response",
                value={
                    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9....",
                    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9....",
                },
                response_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

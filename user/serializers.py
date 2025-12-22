from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    """Public user fields returned in auth responses."""

    class Meta:
        model = User
        fields = ("id", "email", "phone_number", "date_joined")


class RegisterSerializer(serializers.Serializer):
    """Create a user with email login + password."""

    email = serializers.EmailField()
    phone_number = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=15)
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    def validate_phone_number(self, value: str | None) -> str | None:
        # Important: unique=True + blank strings can cause only ONE user to have "".
        # Convert "" to None so multiple users can omit phone_number safely.
        if value == "":
            return None
        return value

    def validate(self, attrs: dict) -> dict:
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    def create(self, validated_data: dict):
        validated_data.pop("password2")
        password = validated_data.pop("password")

        # Your CustomUserManager should implement create_user(email=..., password=...)
        user = User.objects.create_user(password=password, **validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Optional custom claims:
        token["email"] = user.email
        token["is_staff"] = bool(getattr(user, "is_staff", False))
        return token
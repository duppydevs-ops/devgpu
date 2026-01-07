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

    def validate_email(self, value):
        value = value.lower().strip()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_phone_number(self, value):
        if value in (None, ""):
            return value  # allow blank/null as your model allows it

        value = value.strip()
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
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


class ChargeBalanceSerializer(serializers.Serializer):
    amount = serializers.IntegerField(min_value=1)

class ChargeBalanceResponseSerializer(serializers.Serializer):
    balance = serializers.IntegerField()
    charged = serializers.IntegerField()
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from ..models import User


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)
    id = serializers.UUIDField(read_only=True)
    first_name = serializers.CharField(max_length=255, read_only=True)
    last_name = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        fields = [
            'id', 'email', 'password', 'first_name', 'last_name',
            'access_token', 'refresh_token'
        ]

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Authenticate user
        user = authenticate(email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid email or password. Please try again.")
        if not user.is_active:
            raise AuthenticationFailed("Your account is deactivated. Please contact support.")
        if not user.is_verified:
            raise AuthenticationFailed("Your email is not verified.")

        # Retrieve tokens
        tokens = user.tokens()

        return {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'access_token': tokens.get('access'),
            'refresh_token': tokens.get('refresh')
        }

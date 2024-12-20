from django.utils import timezone
from rest_framework import serializers
from ..models import User
import datetime


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'username', 'email', 'password', 'password2',
            'date_of_birth', 'sex'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
            'username': {'required': True},
        }

    def validate(self, attrs):
        password = attrs.get('password', '')
        password2 = attrs.get('password2', '')

        if password != password2:
            raise serializers.ValidationError({"password": "Passwords do not match."})

        # Validate date_of_birth
        date_of_birth = attrs.get('date_of_birth')
        if date_of_birth:
            today = timezone.now().date()
            if isinstance(date_of_birth, datetime.datetime):
                date_of_birth = date_of_birth.date()

            if date_of_birth >= today:
                raise serializers.ValidationError({"date_of_birth": "Date of birth cannot be today or in the future."})

            age = today.year - date_of_birth.year - (
                (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
            )
            if age <= 0:
                raise serializers.ValidationError({"age": "Age must be a positive number greater than 0."})

            attrs['age'] = age

        return attrs

    def create(self, validated_data):
        # Remove password2 as it's only used for validation
        validated_data.pop('password2')

        password = validated_data.pop('password')

        # Create the user
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()

        return user

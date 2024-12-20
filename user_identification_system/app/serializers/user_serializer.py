from rest_framework import serializers
from ..models import User

class BaseSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    def _validate_update_dates(self, initial_data):

        if 'updated_at' in initial_data and 'created_at' in initial_data:
            raise serializers.ValidationError(
                {
                    "updated_at": "You cannot update the update date.",
                    "created_at": "You cannot update the creation date."
                }
            )
        elif 'updated_at' in initial_data:
            raise serializers.ValidationError(
                {"updated_at": "You cannot update the update date."}
            )
        elif 'created_at' in initial_data:
            raise serializers.ValidationError(
                {"created_at": "You cannot update the creation date."}
            )

class UserSerializer(BaseSerializer):
    password = serializers.CharField(write_only = True)
    is_staff = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)
    detail_url = serializers.HyperlinkedIdentityField(
        view_name='user-detail',
        lookup_field='id',
        read_only=True
        )
    class Meta:
        model = User
        fields = '__all__'

    def update(self, instance, validated_data):
        self._validate_update_dates(self.initial_data)
        instance.username = validated_data.get("username", instance.username)
        instance.email = validated_data.get("email", instance.email)
        instance.phone = validated_data.get("phone", instance.phone)
        instance.location = validated_data.get("location", instance.location)
        instance.save()
        return instance
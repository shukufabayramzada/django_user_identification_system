from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils.translation import gettext_lazy as _

class LogoutUserSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()

    default_error_messages = {
        'required': _('Refresh token is required'),
        'bad_token': _('Token is invalid or has expired'),
    }

    def validate(self, attrs):
        self.token = attrs.get('refresh_token')

        if not self.token:
            raise serializers.ValidationError(
                self.default_error_messages['required'], code='required'
            )

        return attrs

    def save(self, **kwargs):
        try:
            token = RefreshToken(self.token)
            token.blacklist()
        except TokenError:
            raise serializers.ValidationError(
                self.default_error_messages['bad_token'], code='bad_token'
            )

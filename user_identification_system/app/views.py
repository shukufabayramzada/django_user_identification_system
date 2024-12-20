import pyotp
from rest_framework.generics import GenericAPIView
from app.serializers.register_serializer import UserRegisterSerializer
from app.serializers.login_serializer import LoginSerializer
from rest_framework.response import Response
from rest_framework import status          
from .models import User, OneTimePassword
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from app.serializers.user_serializer import UserSerializer
from app.serializers.verify_otp_serializer import VerifyOTPSerializer
from app.serializers.swaggerdummy_serializer import SwaggerDummySerializer
from app.serializers.logout_serializer import LogoutUserSerializer
from rest_framework import status, serializers
from django.shortcuts import get_object_or_404
from .utils import  resend_code_to_user
from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from django.conf import settings
from django.core.mail import send_mail


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'

    def deactivate_user(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['id'])
        user.is_active = False
        user.save()
        return Response({'status': 'user deactivated'})
      
    def activate_user(self, request, *args, **kwargs):
        user = get_object_or_404(User, id=kwargs['id'])
        user.is_active = True
        user.save()
        return Response({'status': 'user activated'})
    
class RegisterUserView(APIView):
    serializer_class = UserRegisterSerializer
    
    def post(self, request):
        user_data = request.data
        serializer = self.serializer_class(data=user_data)
        context = {}
        
        if serializer.is_valid(raise_exception=True):
            user_instance = serializer.save()
            secret = pyotp.random_base32()
            otp_code = pyotp.TOTP(secret, interval=120).now()

            # Store the OTP and secret in the database
            OneTimePassword.objects.update_or_create(
                user=user_instance,
                defaults={'otp': otp_code, 'secret': secret, 'created_at': timezone.now()}
            )
            
            subject = 'Welcome to Sanorium'
            message = f'Hi {user_instance.first_name}, thank you for registering in Sanorium. Your OTP code for email verification is: {otp_code}'
            email = user_instance.email
            
            if subject and message and email:
                try:
                    send_mail(subject, message, settings.EMAIL_HOST_USER, [email], fail_silently=False)
                    context['message'] = 'OTP verification code has been sent to your email'
                except Exception as e:
                    context['message'] = 'OTP verification code could not be sent'
            else:
                context['message'] = 'All fields are required'
            
            return Response({
                'data': serializer.data,
                'message': 'Thanks for signing up. An OTP code has been sent to verify your email'
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Existing view for verifying the user's email
class VerifyUserEmail(GenericAPIView):
    serializer_class = VerifyOTPSerializer
    
    def post(self, request):
        otp_code = request.data.get('otp')
        try:
            user_code_obj = OneTimePassword.objects.get(otp=otp_code)
            user = user_code_obj.user

            # Check if the OTP has expired (set to 2 minutes)
            expiry_time = user_code_obj.created_at + timedelta(minutes=2)
            if timezone.now() > expiry_time:
                return Response({
                    'message': 'OTP has expired. Please request a new one.'
                }, status=status.HTTP_400_BAD_REQUEST)

            # Verify the OTP
            test = pyotp.TOTP(user_code_obj.secret, interval=120)
            if test.verify(otp_code, valid_window=1):
                if not user.is_verified:
                    user.is_verified = True
                    user.save()
                    return Response({
                        'message': 'Account email is verified successfully'
                    }, status=status.HTTP_200_OK)
                return Response({
                    'message': 'User is already verified'
                }, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({
                    'message': 'Invalid OTP code'
                }, status=status.HTTP_400_BAD_REQUEST)
            
        except OneTimePassword.DoesNotExist:
            return Response({
                'message': 'OTP does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

# New view for resending the OTP code
class ResendOtpView(GenericAPIView):

    def get_serializer_class(self):
        if getattr(self, 'swagger_fake_view', False):
            return SwaggerDummySerializer 
        return super().get_serializer_class()

    def post(self, request):
        email = request.data.get('email')
        try:
            user = User.objects.get(email=email)
            if user.is_verified:
                return Response({
                    'message': 'User is already verified'
                }, status=status.HTTP_400_BAD_REQUEST)

            resend_code_to_user(email)  # Resend OTP Code
            return Response({
                'message': 'A new OTP has been sent to your email'
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({
                'message': 'User with this email does not exist'
            }, status=status.HTTP_404_NOT_FOUND)

class LoginUserView(GenericAPIView):
    serializer_class=LoginSerializer
    # Post request for getting login data
    def post(self, request):
        serializer=self.serializer_class(data=request.data, context={'request' :request})
        
        # Check for serializer is valid or not:
        serializer.is_valid(raise_exception=True)
        
        # If it is valid then we genearate token for user.
        # Response returning:
        return Response(serializer.data, status=status.HTTP_200_OK)

# Endpoint for testing token 
class TestAuthenticationView(GenericAPIView):
    serializer_class = SwaggerDummySerializer
    permission_classes=[IsAuthenticated]
    
    def get(self, request):
        data={
            'message': "It is working"
        }
        return Response(data, status=status.HTTP_200_OK)
    

class LogoutUserView(GenericAPIView):
    serializer_class = LogoutUserSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            serializer.save()
            return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)
        
        except serializers.ValidationError as e:
            # Handles specific validation errors if needed
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            # General error handler for unexpected issues
            return Response(
                {"detail": "An error occurred during logout. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


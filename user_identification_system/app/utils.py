import pyotp
from django.core.mail import EmailMessage
from django.conf import settings
from django.utils import timezone
from .models import User, OneTimePassword

def generateOtp(secret):
    totp = pyotp.TOTP(secret, interval=120)
    return totp.now()  # Generate OTP based on the secret

def send_code_to_user(email):
    user = User.objects.get(email=email)
    # Create a unique secret for the user
    secret = pyotp.random_base32()  # Generate a base32 secret
    otp_code = pyotp.TOTP(secret, interval=120).now()
    
    # Create or update the OTP record
    OneTimePassword.objects.update_or_create(user=user, defaults={'otp': otp_code, 'secret': secret, 'created_at': timezone.now()})

    # Email logic
    current_site = "sanorium.com"
    email_body = f"Hi {user.first_name}, thanks for signing up on {current_site}. Please verify your email with the one-time passcode: {otp_code}."
    from_email = settings.DEFAULT_FROM_EMAIL

    d_email = EmailMessage(subject="One time passcode for email verification", body=email_body, from_email=from_email, to=[user.email])
    d_email.send(fail_silently=True)


def resend_code_to_user(email):
    user = User.objects.get(email=email)
    secret = pyotp.random_base32()  # Generate a new base32 secret
    otp_code = generateOtp(secret)
    
    # Update the OTP record with a new code and secret
    OneTimePassword.objects.update_or_create(user=user, defaults={'otp': otp_code, 'secret': secret, 'created_at': timezone.now()})
    current_site = "sanorium.com"
    email_body = f"Hi {user.first_name}, here is your new one-time passcode: {otp_code}. Please use it to verify your email."
    from_email = settings.DEFAULT_FROM_EMAIL

    d_email = EmailMessage(subject="New One-Time Passcode for Email Verification", body=email_body, from_email=from_email, to=[user.email])
    d_email.send(fail_silently=True)
    
def send_normal_email(data):
    email=EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        from_email=settings.EMAIL_HOST_USER,
        to=[data['to_email']]
    )
    email.send()
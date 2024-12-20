from django.db import models
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
import uuid
from django.utils import timezone
from app.user_manager import UserManager
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime

class User(AbstractBaseUser, PermissionsMixin):
    class UserSex(models.TextChoices):
        M = "MALE", "Male"
        F = "FEMALE", "Female"
        O = "OTHER", "Other"
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField(null=True)
    sex = models.CharField(max_length=6, choices=UserSex.choices)
    date_of_birth = models.DateField(null=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ["first_name", "last_name", "age", "sex", "date_of_birth"]

    objects = UserManager()

    def save(self, *args, **kwargs):
        if isinstance(self.date_of_birth, str):
            self.date_of_birth = datetime.strptime(self.date_of_birth, "%Y-%m-%d")
        
        if self.date_of_birth:
            today = timezone.now().date()
            self.age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.email

    @property
    def get_full_name(self):
        return f"{self.first_name.title()} {self.last_name.title()}"

    def tokens(self):
        refresh = RefreshToken.for_user(self)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }

class OneTimePassword(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    secret = models.CharField(max_length=64, unique=True, default='initial_unique_secret')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.first_name} - OTP Code"
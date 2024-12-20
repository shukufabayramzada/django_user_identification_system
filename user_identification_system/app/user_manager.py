from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def email_validator(self, email):
        try:
            self.validate_email(email)
        except ValidationError:
            raise ValueError(_("Please provide a valid email address"))
    
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("An email address is required"))
        
        email = self.normalize_email(email)
        self.email_validator(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError(_("Superuser must have is_staff=True."))
        if not extra_fields.get('is_superuser'):
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self.create_user(email, password, **extra_fields)

import uuid
import re
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_nigerian_phone(value):
    """
    Validates standard Nigerian telephone numbers:
    Format: 080..., 070..., 081..., 090..., 091..., or international +234...
    """
    if not value:
        return
    cleaned = re.sub(r'[\s\-()]', '', value)
    pattern = r'^(?:\+234|234|0)[789][01]\d{8}$'
    if not re.match(pattern, cleaned):
        raise ValidationError("Enter a valid Nigerian phone number (e.g. 08012345678 or +2348012345678).")


class UserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier for authentication.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('An email address is required.')
        email = self.normalize_email(email).lower()
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        extra_fields.setdefault('is_verified', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model supporting three primary roles: Agent, Buyer/Renter, and Admin.
    """
    class Role(models.TextChoices):
        AGENT = 'agent', 'Property Agent'
        BUYER = 'buyer', 'Buyer / Renter'
        ADMIN = 'admin', 'Administrator'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255, db_index=True)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=25, validators=[validate_nigerian_phone], blank=True, null=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.BUYER, db_index=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False, help_text="Email verification status.")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.full_name} ({self.get_role_display()})"

    @property
    def is_agent(self):
        return self.role == self.Role.AGENT

    @property
    def is_buyer(self):
        return self.role == self.Role.BUYER

    @property
    def is_administrator(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def display_avatar(self):
        if self.profile_image and hasattr(self.profile_image, 'url'):
            return self.profile_image.url
        return None

    def clean_phone_number(self):
        if not self.phone_number:
            return ""
        digits = re.sub(r'\D', '', self.phone_number)
        if digits.startswith('234') and len(digits) == 13:
            return f"+{digits}"
        if digits.startswith('0') and len(digits) == 11:
            return f"+234{digits[1:]}"
        return self.phone_number


class AgentProfile(models.Model):
    """
    Extended business profile for Property Agents.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    agency_name = models.CharField(max_length=255, help_text="Real estate firm or brand name.")
    license_number = models.CharField(max_length=100, blank=True, null=True, help_text="REDAN or CAC registration number.")
    biography = models.TextField(blank=True, default="", help_text="Agent experience, specialties, and bio.")
    office_address = models.CharField(max_length=255, blank=True, default="")
    state = models.CharField(max_length=100, default="Nasarawa")
    city = models.CharField(max_length=100, default="Keffi")
    whatsapp_number = models.CharField(max_length=25, blank=True, default="")
    is_verified_agent = models.BooleanField(default=False, help_text="Badge awarded upon credential validation.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Agent Profile'
        verbose_name_plural = 'Agent Profiles'

    def __str__(self):
        return f"{self.agency_name} - {self.user.full_name}"


class BuyerProfile(models.Model):
    """
    Preferences and profile details for Buyers and Renters.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')
    preferred_state = models.CharField(max_length=100, blank=True, default="Nasarawa")
    preferred_city = models.CharField(max_length=100, blank=True, default="Keffi")
    max_budget = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Buyer Profile'
        verbose_name_plural = 'Buyer Profiles'

    def __str__(self):
        return f"Buyer Profile: {self.user.full_name}"

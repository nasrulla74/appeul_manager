from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class ServerStatus(models.Model):
    is_running = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

class BackupLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    filename = models.CharField(max_length=255)
    success = models.BooleanField()
    output = models.TextField(blank=True)
    error = models.TextField(blank=True)

    def __str__(self):
        return f"{self.timestamp} - {'Success' if self.success else 'Failure'}"

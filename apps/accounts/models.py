from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
        ('therapist', 'Therapist'),
        ('moderator', 'Moderator'),
    ]

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150, blank=True)
    display_name = models.CharField(max_length=100, blank=True, null=True)
    avatar_url = models.CharField(max_length=500, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    streak_days = models.IntegerField(default=0)
    wellness_score = models.IntegerField(default=50)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True)
    emergency_contact_phone = models.CharField(max_length=50, blank=True, null=True)
    last_active = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    @property
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser or self.is_staff

    @property
    def avatar_display_url(self):
        if self.avatar_url:
            if self.avatar_url.startswith(('https://', 'http://')):
                return self.avatar_url
            if not getattr(settings, 'IS_VERCEL', False):
                if self.avatar_url.startswith('/'):
                    return self.avatar_url
                return f'/{self.avatar_url}'
        if getattr(settings, 'IS_VERCEL', False):
            return None
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return None

    @property
    def display_title(self):
        if self.display_name:
            return self.display_name
        if self.full_name:
            return self.full_name
        return self.username


class UserSettings(models.Model):
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('auto', 'Auto'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    theme = models.CharField(max_length=10, choices=THEME_CHOICES, default='light')
    notifications_enabled = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=True)
    weekly_summary_day = models.CharField(max_length=20, default='sunday')
    data_sharing_level = models.CharField(max_length=20, default='anonymous')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Settings for {self.user.username}"


class UserActivityLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='activity_logs')
    action = models.CharField(max_length=100)
    details = models.TextField(blank=True, null=True)
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"{username}: {self.action} at {self.created_at}"

from django.db import models
from django.conf import settings

class Therapist(models.Model):
    name = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True)
    whatsapp = models.CharField(max_length=50, blank=True)
    website = models.CharField(max_length=255, blank=True)
    profile_image = models.CharField(max_length=500, blank=True)
    credentials = models.TextField(blank=True)
    experience_years = models.IntegerField(default=0)
    languages_spoken = models.CharField(max_length=255, blank=True, default='English, Swahili')
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_verified = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'display_order', 'name']

    def __str__(self):
        return self.name


class TherapySession(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='therapy_sessions')
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, related_name='sessions')
    session_date = models.DateField()
    session_time = models.TimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-session_date']

    def __str__(self):
        return f"{self.user.username} with {self.therapist.name} on {self.session_date}"


class TherapyResource(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, default='General')
    url = models.CharField(max_length=500, blank=True)
    resource_type = models.CharField(max_length=50, default='article')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

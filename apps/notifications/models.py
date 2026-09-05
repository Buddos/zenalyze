from django.db import models
from django.conf import settings

class Notification(models.Model):
    TYPE_CHOICES = [
        ('system', 'System'),
        ('reminder', 'Reminder'),
        ('achievement', 'Achievement'),
        ('community', 'Community'),
        ('mood', 'Mood'),
        ('journal', 'Journal'),
        ('wellness', 'Wellness'),
        ('quote', 'Quote'),
        ('crisis', 'Crisis'),
        ('message', 'Message'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='system')
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    link = models.CharField(max_length=500, blank=True, null=True)
    icon = models.CharField(max_length=50, default='bell')
    is_read = models.BooleanField(default=False)
    is_global = models.BooleanField(default=False)
    priority = models.CharField(max_length=20, default='normal')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.type}] {self.title}"

    @property
    def icon_class(self):
        icon_map = {
            'system': 'bi-gear',
            'reminder': 'bi-bell',
            'achievement': 'bi-trophy',
            'community': 'bi-people',
            'mood': 'bi-emoji-smile',
            'journal': 'bi-journal-text',
            'wellness': 'bi-heart',
            'quote': 'bi-quote',
            'crisis': 'bi-exclamation-triangle',
            'message': 'bi-chat',
        }
        return icon_map.get(self.type, 'bi-bell')


class UserReminder(models.Model):
    TYPE_CHOICES = [
        ('mood', 'Mood'),
        ('journal', 'Journal'),
        ('exercise', 'Exercise'),
        ('meditation', 'Meditation'),
        ('water', 'Water'),
        ('sleep', 'Sleep'),
        ('custom', 'Custom'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminders')
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    reminder_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='custom')
    reminder_time = models.TimeField(null=True, blank=True)
    reminder_date = models.DateField(null=True, blank=True)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    last_sent = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} Reminder: {self.title}"


class Announcement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    type = models.CharField(max_length=50, default='info')
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

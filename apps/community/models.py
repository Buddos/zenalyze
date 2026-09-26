from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator


class MediaAsset(models.Model):
    TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
    ]
    PROCESSING_CHOICES = [
        ('uploading', 'Uploading'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('failed', 'Failed'),
    ]

    asset_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    file = models.FileField(
        upload_to='media-assets/%Y/%m/',
        validators=[FileExtensionValidator(allowed_extensions=[
            'jpg', 'jpeg', 'png', 'gif', 'webp', 'mp4', 'webm', 'ogv', 'mov', 'mp3', 'm4a', 'ogg', 'wav',
        ])],
    )
    thumbnail = models.ImageField(upload_to='media-assets/thumbnails/%Y/%m/', blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='uploaded_media')
    processing_status = models.CharField(max_length=12, choices=PROCESSING_CHOICES, default='ready')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.get_asset_type_display()}: {self.file.name}'


class PostMedia(models.Model):
    post = models.ForeignKey('CommunityPost', on_delete=models.CASCADE, related_name='media_items')
    media_asset = models.ForeignKey(MediaAsset, on_delete=models.CASCADE, related_name='post_links')
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['position', 'id']
        constraints = [
            models.UniqueConstraint(fields=['post', 'position'], name='unique_post_media_position'),
        ]

class CommunityPost(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('hidden', 'Hidden'),
        ('deleted', 'Deleted'),
    ]
    MODERATION_STATUS_CHOICES = [
        ('pending', 'Pending review'),
        ('visible', 'Visible'),
        ('removed', 'Removed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_posts')
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    category = models.CharField(max_length=100, default='General')
    is_anonymous = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)
    report_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    moderation_status = models.CharField(max_length=12, choices=MODERATION_STATUS_CHOICES, default='visible')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return self.title or f'Post by {self.user.username}'

    @property
    def author_display(self):
        if self.is_anonymous:
            return "Anonymous"
        return self.user.display_title


class PostComment(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_comments')
    content = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment on {self.post.title}"

    @property
    def author_display(self):
        if self.is_anonymous:
            return "Anonymous"
        return self.user.display_title


class PostLike(models.Model):
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='post_likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')

    def __str__(self):
        return f"{self.user.username} likes {self.post.title}"


class CommunityMessage(models.Model):
    TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('emoji', 'Emoji'),
        ('system', 'System'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='community_messages')
    message = models.TextField()
    message_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='text')
    image_url = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message[:30]}"


class AnonymousChatSession(models.Model):
    STATUS_CHOICES = [
        ('waiting', 'Waiting'),
        ('active', 'Active'),
        ('ended', 'Ended'),
    ]

    session_code = models.CharField(max_length=32, unique=True)
    participant1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='anon_sessions_1')
    participant2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='anon_sessions_2')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    topic = models.CharField(max_length=80, default='General Support', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Anon Session {self.session_code} ({self.status})"


class AnonymousMessage(models.Model):
    session = models.ForeignKey(AnonymousChatSession, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message_text = models.TextField()
    is_anonymous = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Msg in {self.session.session_code}"


class AIChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ai_chats')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role}: {self.message[:30]}"

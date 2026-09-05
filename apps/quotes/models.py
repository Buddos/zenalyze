from django.db import models
from django.conf import settings

class Quote(models.Model):
    quote_text = models.TextField()
    author = models.CharField(max_length=255, default='Unknown')
    category = models.CharField(max_length=50, default='General')
    language = models.CharField(max_length=10, default='en')
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'"{self.quote_text[:40]}..." — {self.author}'


class QuoteUserInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quote_interactions')
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE, related_name='interactions')
    is_favorite = models.BooleanField(default=False)
    is_viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'quote')

    def __str__(self):
        return f"{self.user.username} - Quote {self.quote.id} (Fav: {self.is_favorite})"


class DailyQuoteView(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='daily_quote_views')
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-viewed_at']

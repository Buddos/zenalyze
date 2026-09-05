from django.db import models
from django.conf import settings

class MoodEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='mood_entries')
    mood_score = models.IntegerField(default=5)  # 1 to 10
    primary_emotion = models.CharField(max_length=100, blank=True)
    secondary_emotion = models.CharField(max_length=100, blank=True)
    stress_level = models.IntegerField(default=5)  # 1 to 10
    energy_level = models.IntegerField(default=5)  # 1 to 10
    sleep_quality = models.IntegerField(default=3)  # 1 to 5
    triggers_factors = models.TextField(blank=True)
    gratitude = models.TextField(blank=True)
    journal_entry = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - Mood {self.mood_score} on {self.created_at.strftime('%Y-%m-%d')}"

    @property
    def emoji(self):
        score_map = {
            1: '😢', 2: '😫', 3: '😔', 4: '😕', 5: '😐',
            6: '🙂', 7: '😊', 8: '😄', 9: '🤩', 10: '😄'
        }
        em = self.primary_emotion.lower() if self.primary_emotion else ''
        if 'happy' in em or 'joy' in em: return '😊'
        if 'excited' in em or 'energetic' in em: return '🤩'
        if 'calm' in em or 'peaceful' in em: return '😌'
        if 'grateful' in em or 'blessed' in em: return '🙏'
        if 'sad' in em: return '😢'
        if 'anxious' in em or 'worried' in em: return '😰'
        if 'angry' in em or 'frustrated' in em: return '😤'
        if 'tired' in em or 'exhausted' in em: return '😴'
        if 'stressed' in em: return '😫'
        if 'loved' in em or 'love' in em: return '❤️'
        return score_map.get(self.mood_score, '😐')


class JournalEntry(models.Model):
    ENTRY_TYPE_CHOICES = [
        ('reflection', 'Reflection'),
        ('gratitude', 'Gratitude'),
        ('goal', 'Goal'),
        ('dream', 'Dream'),
        ('creative', 'Creative'),
        ('daily_log', 'Daily Log'),
        ('free_write', 'Free Write'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='journal_entries')
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    entry_type = models.CharField(max_length=30, choices=ENTRY_TYPE_CHOICES, default='reflection')
    mood = models.CharField(max_length=50, blank=True)
    mood_before = models.CharField(max_length=50, blank=True)
    mood_after = models.CharField(max_length=50, blank=True)
    energy_level = models.IntegerField(default=5)
    tags = models.CharField(max_length=500, blank=True)
    is_private = models.BooleanField(default=True)
    is_favorite = models.BooleanField(default=False)
    word_count = models.IntegerField(default=0)
    gratitude_list = models.TextField(blank=True)
    goals = models.TextField(blank=True)
    dreams_notes = models.TextField(blank=True)
    location = models.CharField(max_length=255, blank=True)
    weather = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title or f"Journal on {self.created_at.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        if self.content:
            self.word_count = len(self.content.split())
        super().save(*args, **kwargs)


class Exercise(models.Model):
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=100, default='meditation')
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    duration_minutes = models.IntegerField(default=5)
    video_url = models.CharField(max_length=500, blank=True)
    video_type = models.CharField(max_length=20, default='youtube')
    thumbnail_image = models.CharField(max_length=500, blank=True)
    instructions = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    is_guided = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_featured', 'display_order', '-created_at']

    def __str__(self):
        return self.title


class UserExerciseSession(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='exercise_sessions')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='sessions')
    duration_minutes = models.IntegerField(default=0)
    completed = models.BooleanField(default=True)
    mood_before = models.IntegerField(default=5)
    mood_after = models.IntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.exercise.title} ({self.duration_minutes}m)"


class DailyMotivation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='motivations', null=True, blank=True)
    text = models.TextField()
    motivation_type = models.CharField(max_length=50, default='affirmation')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]


class FinancialEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='financial_entries')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=50)  # Income, Housing, Food, Transportation, Health, etc.
    subcategory = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    currency = models.CharField(max_length=3, default='KES')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.currency} {self.amount} ({self.category})"


class RelationshipEntry(models.Model):
    RELATIONSHIP_TYPES = [
        ('family', 'Family'),
        ('friend', 'Friend'),
        ('partner', 'Partner'),
        ('colleague', 'Colleague'),
        ('other', 'Other'),
    ]
    ENERGY_CHOICES = [
        ('energizing', 'Energizing'),
        ('neutral', 'Neutral'),
        ('draining', 'Draining'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='relationship_entries')
    person_name = models.CharField(max_length=100)
    relationship_type = models.CharField(max_length=50, choices=RELATIONSHIP_TYPES)
    interaction_quality = models.IntegerField(default=5)  # 1 to 10
    emotional_energy = models.CharField(max_length=20, choices=ENERGY_CHOICES, default='neutral')
    notes = models.TextField(blank=True)
    mood_before = models.IntegerField(null=True, blank=True)
    mood_after = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.person_name} ({self.relationship_type})"


class WellnessGoal(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='goals')
    goal_type = models.CharField(max_length=50)  # mood_tracking, exercise_minutes, journal_entries, etc.
    target_value = models.IntegerField()
    current_value = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Goal: {self.goal_type} ({self.current_value}/{self.target_value})"

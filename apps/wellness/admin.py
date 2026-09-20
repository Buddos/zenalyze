from django.contrib import admin
from .models import (
    MoodEntry,
    JournalEntry,
    Exercise,
    UserExerciseSession,
    DailyMotivation,
    FinancialEntry,
    RelationshipEntry,
    WellnessGoal,
)


@admin.register(MoodEntry)
class MoodEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'mood_score', 'primary_emotion', 'stress_level', 'energy_level', 'created_at')
    list_filter = ('mood_score', 'primary_emotion', 'created_at')
    search_fields = ('user__username', 'primary_emotion', 'secondary_emotion', 'journal_entry')
    date_hierarchy = 'created_at'


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'entry_type', 'mood', 'is_favorite', 'created_at')
    list_filter = ('entry_type', 'is_favorite', 'created_at')
    search_fields = ('user__username', 'title', 'content')
    date_hierarchy = 'created_at'


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'difficulty_level', 'duration_minutes', 'is_featured', 'is_active')
    list_filter = ('category', 'difficulty_level', 'is_featured', 'is_active')
    search_fields = ('title', 'description', 'benefits')


@admin.register(UserExerciseSession)
class UserExerciseSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'exercise', 'duration_minutes', 'completed', 'created_at')
    list_filter = ('completed', 'created_at')
    search_fields = ('user__username', 'exercise__title')


@admin.register(DailyMotivation)
class DailyMotivationAdmin(admin.ModelAdmin):
    list_display = ('user', 'text_preview', 'motivation_type', 'is_completed', 'created_at')
    list_filter = ('motivation_type', 'is_completed', 'created_at')
    search_fields = ('text', 'user__username')

    def text_preview(self, obj):
        return obj.text[:50] if obj.text else ''
    text_preview.short_description = 'Motivation Text'


@admin.register(FinancialEntry)
class FinancialEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'currency', 'created_at')
    list_filter = ('category', 'currency', 'created_at')
    search_fields = ('user__username', 'category', 'description')


@admin.register(RelationshipEntry)
class RelationshipEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'person_name', 'relationship_type', 'interaction_quality', 'emotional_energy', 'created_at')
    list_filter = ('relationship_type', 'emotional_energy', 'created_at')
    search_fields = ('user__username', 'person_name', 'notes')


@admin.register(WellnessGoal)
class WellnessGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal_type', 'target_value', 'current_value', 'created_at')
    list_filter = ('goal_type', 'created_at')
    search_fields = ('user__username', 'goal_type')

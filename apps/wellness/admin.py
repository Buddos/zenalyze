from django.contrib import admin
from django import forms
from django.utils import timezone
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
from .models import Exercise


class ExerciseAdminForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('status') != 'published':
            return cleaned_data

        media_asset = cleaned_data.get('media_asset')
        has_legacy_media = cleaned_data.get('video_file') or cleaned_data.get('video_url')
        has_guided_content = cleaned_data.get('is_guided') or cleaned_data.get('instructions')
        if media_asset and media_asset.processing_status != 'ready':
            self.add_error('media_asset', 'Practice media must finish processing before it can be published.')
        elif not (media_asset or has_legacy_media or has_guided_content):
            raise forms.ValidationError('Add practice media or guided instructions before publishing.')
        return cleaned_data


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
    form = ExerciseAdminForm
    list_display = ('title', 'category', 'difficulty_level', 'duration_minutes', 'status', 'media_asset', 'is_featured', 'is_active')
    list_filter = ('status', 'category', 'difficulty_level', 'is_featured', 'is_active')
    search_fields = ('title', 'description', 'benefits')
    autocomplete_fields = ('media_asset',)
    readonly_fields = ('published_at',)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        initial.setdefault('status', 'draft')
        return initial

    def save_model(self, request, obj, form, change):
        if not obj.created_by_id:
            obj.created_by = request.user
        if obj.status == 'published':
            if not obj.published_at:
                obj.published_at = timezone.now()
        else:
            obj.published_at = None
        super().save_model(request, obj, form, change)


@admin.register(UserExerciseSession)
class UserExerciseSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'exercise', 'progress_seconds', 'duration_minutes', 'completed', 'started_at', 'created_at')
    list_filter = ('completed', 'started_at', 'created_at')
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

from django.contrib import admin
from .models import Therapist, TherapySession, TherapyResource


@admin.register(Therapist)
class TherapistAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'email', 'phone', 'experience_years', 'consultation_fee', 'is_verified', 'is_featured', 'is_active')
    list_filter = ('is_verified', 'is_featured', 'is_active')
    search_fields = ('name', 'specialization', 'email', 'phone', 'credentials')


@admin.register(TherapySession)
class TherapySessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'therapist', 'session_date', 'session_time', 'duration_minutes', 'status', 'created_at')
    list_filter = ('status', 'session_date')
    search_fields = ('user__username', 'therapist__name', 'notes')


@admin.register(TherapyResource)
class TherapyResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'resource_type', 'is_active', 'created_at')
    list_filter = ('category', 'resource_type', 'is_active')
    search_fields = ('title', 'description', 'url')

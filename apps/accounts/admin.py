from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserSettings, UserActivityLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'full_name', 'role', 'is_staff', 'is_active', 'streak_days', 'wellness_score', 'last_active')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'full_name')
    ordering = ('username',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile & Wellness', {
            'fields': (
                'full_name',
                'display_name',
                'role',
                'avatar_url',
                'avatar',
                'streak_days',
                'wellness_score',
                'emergency_contact_name',
                'emergency_contact_phone',
            )
        }),
    )


@admin.register(UserSettings)
class UserSettingsAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'notifications_enabled', 'email_notifications', 'created_at')
    list_filter = ('theme', 'notifications_enabled', 'email_notifications')
    search_fields = ('user__username', 'user__email')


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__username', 'action', 'details', 'ip_address')
    readonly_fields = ('created_at',)

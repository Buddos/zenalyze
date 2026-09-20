from django.contrib import admin
from .models import (
    SystemSetting,
    ContentModeration,
    CrisisAlert,
    CrisisResponse,
    CrisisResource,
    TeamMember,
    ContactMessage,
)


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('setting_key', 'setting_value', 'updated_at')
    search_fields = ('setting_key', 'setting_value')


@admin.register(ContentModeration)
class ContentModerationAdmin(admin.ModelAdmin):
    list_display = ('content_type', 'content_id', 'reported_by', 'reason', 'status', 'moderated_by', 'created_at')
    list_filter = ('status', 'content_type', 'created_at')
    search_fields = ('reason', 'description', 'moderator_notes')


@admin.register(CrisisAlert)
class CrisisAlertAdmin(admin.ModelAdmin):
    list_display = ('title', 'severity', 'is_active', 'expires_at', 'created_by', 'created_at')
    list_filter = ('severity', 'is_active', 'created_at')
    search_fields = ('title', 'message')


@admin.register(CrisisResponse)
class CrisisResponseAdmin(admin.ModelAdmin):
    list_display = ('alert', 'user', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('response_text', 'user__username', 'alert__title')


@admin.register(CrisisResource)
class CrisisResourceAdmin(admin.ModelAdmin):
    list_display = ('resource_name', 'phone_number', 'sms_number', 'category', 'priority', 'is_active')
    list_filter = ('category', 'priority', 'is_active')
    search_fields = ('resource_name', 'phone_number', 'description')


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'role', 'initials', 'display_order', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'role', 'bio')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')

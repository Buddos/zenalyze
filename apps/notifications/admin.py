from django.contrib import admin
from .models import Notification, UserReminder, Announcement


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'type', 'priority', 'is_read', 'is_global', 'created_at')
    list_filter = ('type', 'priority', 'is_read', 'is_global', 'created_at')
    search_fields = ('title', 'message', 'user__username')


@admin.register(UserReminder)
class UserReminderAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'reminder_type', 'reminder_time', 'is_recurring', 'is_active')
    list_filter = ('reminder_type', 'is_recurring', 'is_active')
    search_fields = ('title', 'user__username', 'message')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'is_active', 'expires_at', 'created_at')
    list_filter = ('type', 'is_active', 'created_at')
    search_fields = ('title', 'content')

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserSettings, UserActivityLog


class AdminUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'full_name', 'role', 'is_staff', 'is_superuser')

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('is_superuser'):
            cleaned_data['is_staff'] = True
        return cleaned_data


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = AdminUserCreationForm
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'full_name', 'role',
                'password1', 'password2', 'is_staff', 'is_superuser',
            ),
        }),
    )
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

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if request.user.is_superuser:
            return fieldsets

        restricted_fields = {'is_staff', 'is_superuser', 'groups', 'user_permissions'}
        safe_fieldsets = []
        for name, options in fieldsets:
            fields = options.get('fields', ())
            if isinstance(fields, str):
                fields = (fields,)
            visible_fields = tuple(field for field in fields if field not in restricted_fields)
            if visible_fields:
                safe_fieldsets.append((name, {**options, 'fields': visible_fields}))
        return safe_fieldsets


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

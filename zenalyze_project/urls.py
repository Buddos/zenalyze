from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def legacy_redirect(target):
    def view(request):
        return redirect(target, permanent=True)
    return view

# Configure Django Admin Branding
admin.site.site_header = "Zenalyze Administration"
admin.site.site_title = "Zenalyze Admin Portal"
admin.site.index_title = "Zenalyze Management & Database Control"

urlpatterns = [
    # Custom Administration endpoints (must precede admin.site.urls so specific routes like /admin/users/ are caught first)
    path('', include('apps.administration.urls')),

    # Application endpoints
    path('', include('apps.core.urls')),
    path('', include('apps.accounts.urls')),
    path('', include('apps.wellness.urls')),
    path('', include('apps.community.urls')),
    path('', include('apps.quotes.urls')),
    path('', include('apps.therapists.urls')),
    path('', include('apps.notifications.urls')),

    # Django Admin site
    path('admin/', admin.site.urls),
    path('django-admin/', legacy_redirect('/admin/')),

    # Legacy PHP Redirects for seamless backwards compatibility
    path('index.php', legacy_redirect('/')),
    path('about.php', legacy_redirect('/about/')),
    path('contact.php', legacy_redirect('/contact/')),
    path('terms.php', legacy_redirect('/terms/')),
    path('privacy.php', legacy_redirect('/privacy/')),
    path('help.php', legacy_redirect('/help-center/')),
    path('help-center.php', legacy_redirect('/help-center/')),
    path('crisis-help.php', legacy_redirect('/crisis-help/')),
    path('auth/login.php', legacy_redirect('/auth/login/')),
    path('auth/register.php', legacy_redirect('/auth/register/')),
    path('auth/logout.php', legacy_redirect('/auth/logout/')),
    path('auth/forgot-password.php', legacy_redirect('/auth/forgot-password/')),
    path('dashboard.php', legacy_redirect('/dashboard/')),
    path('mood-log.php', legacy_redirect('/mood-log/')),
    path('journal.php', legacy_redirect('/journal/')),
    path('exercises.php', legacy_redirect('/exercises/')),
    path('analytics.php', legacy_redirect('/analytics/')),
    path('history.php', legacy_redirect('/history/')),
    path('financial.php', legacy_redirect('/financial/')),
    path('financial-planner.php', legacy_redirect('/financial/')),
    path('relationships.php', legacy_redirect('/relationships/')),
    path('motivations.php', legacy_redirect('/motivations/')),
    path('generate-report.php', legacy_redirect('/generate-report/')),
    path('community.php', legacy_redirect('/community/')),
    path('community/index.php', legacy_redirect('/community/')),
    path('ai-chat.php', legacy_redirect('/ai-chat/')),
    path('anonymous-chat.php', legacy_redirect('/anonymous-chat/')),
    path('quotes.php', legacy_redirect('/quotes/')),
    path('therapy.php', legacy_redirect('/therapy/')),
    path('notification.php', legacy_redirect('/notifications/')),
    path('notifications.php', legacy_redirect('/notifications/')),
    path('profile.php', legacy_redirect('/profile/')),
    path('settings.php', legacy_redirect('/settings/')),
    path('admin-dashboard.php', legacy_redirect('/admin-dashboard/')),
    path('admin-users.php', legacy_redirect('/admin/users/')),
    path('admin-moderation.php', legacy_redirect('/admin/moderation/')),
    path('admin-crisis-alerts.php', legacy_redirect('/admin/crisis-alerts/')),
    path('admin-settings.php', legacy_redirect('/admin/settings/')),
    path('admin-logs.php', legacy_redirect('/admin/logs/')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

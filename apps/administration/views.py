from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q

from apps.accounts.models import User, UserActivityLog
from apps.wellness.models import MoodEntry
from apps.community.models import CommunityPost
from .models import SystemSetting, ContentModeration, CrisisAlert, CrisisResource

def is_admin_check(user):
    return user.is_authenticated and (user.is_admin_user or user.is_superuser or user.is_staff)

@user_passes_test(is_admin_check, login_url='/auth/login/')
def admin_dashboard_view(request):
    total_users = User.objects.count()
    total_moods = MoodEntry.objects.count()
    total_posts = CommunityPost.objects.count()
    active_alerts = CrisisAlert.objects.filter(is_active=True).count()
    
    stats = {
        'total_users': total_users,
        'total_moods': total_moods,
        'total_posts': total_posts,
        'active_alerts': active_alerts,
    }
    
    recent_users = User.objects.order_by('-date_joined')[:6]
    
    return render(request, 'administration/admin_dashboard.html', {
        'stats': stats,
        'recent_users': recent_users,
    })

@user_passes_test(is_admin_check, login_url='/auth/login/')
def admin_users_view(request):
    query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '')
    
    users = User.objects.all().order_by('-date_joined')
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query) | Q(full_name__icontains=query))
    if role_filter:
        users = users.filter(role=role_filter)
        
    return render(request, 'administration/admin_users.html', {
        'users': users[:50],
        'query': query,
        'role_filter': role_filter,
    })

@user_passes_test(is_admin_check, login_url='/auth/login/')
@require_POST
def toggle_user_status_view(request, user_id):
    u = get_object_or_404(User, id=user_id)
    if u != request.user:
        u.is_active = not u.is_active
        u.save(update_fields=['is_active'])
        messages.success(request, f"User {u.username} status updated to {'Active' if u.is_active else 'Suspended'}.")
    return redirect('administration:users')

@user_passes_test(is_admin_check, login_url='/auth/login/')
def admin_moderation_view(request):
    flagged = ContentModeration.objects.filter(status='pending').select_related('reported_by').order_by('-created_at')[:100]
    return render(request, 'administration/admin_moderation.html', {'flagged_items': flagged})

@user_passes_test(is_admin_check, login_url='/auth/login/')
@require_POST
def review_moderation_view(request, item_id, action):
    item = get_object_or_404(ContentModeration, id=item_id)
    if action == 'approve':
        if item.content_type == 'post':
            post = get_object_or_404(CommunityPost, id=item.content_id)
            if post.media_items.exclude(media_asset__processing_status='ready').exists():
                messages.error(request, 'This post cannot be approved until all media processing is complete.')
                return redirect('administration:moderation')
            if post.moderation_status == 'pending':
                post.moderation_status = 'visible'
                post.save(update_fields=['moderation_status'])
        item.status = 'approved'
    elif action == 'reject':
        item.status = 'rejected'
        if item.content_type == 'post':
            CommunityPost.objects.filter(id=item.content_id).update(status='hidden', moderation_status='removed')
    else:
        messages.error(request, 'Unknown moderation action.')
        return redirect('administration:moderation')
    item.moderated_by = request.user
    item.moderated_at = timezone.now()
    item.save()
    messages.success(request, f"Flagged item #{item.id} has been marked as {item.status}.")
    return redirect('administration:moderation')

@user_passes_test(is_admin_check, login_url='/auth/login/')
def admin_crisis_alerts_view(request):
    alerts = CrisisAlert.objects.all().order_by('-created_at')
    resources = CrisisResource.objects.filter(is_active=True).order_by('-priority')
    return render(request, 'administration/admin_crisis_alerts.html', {
        'alerts': alerts,
        'resources': resources,
    })

@user_passes_test(is_admin_check, login_url='/auth/login/')
@require_POST
def create_crisis_alert_view(request):
    title = request.POST.get('title', '').strip()
    message = request.POST.get('message', '').strip()
    severity = request.POST.get('severity', 'medium')
    
    if title and message:
        CrisisAlert.objects.create(
            title=title,
            message=message,
            severity=severity,
            created_by=request.user,
            is_active=True
        )
        messages.success(request, "Crisis broadcast alert dispatched successfully.")
    return redirect('administration:crisis_alerts')

@user_passes_test(is_admin_check, login_url='/auth/login/')
@require_POST
def toggle_crisis_alert_view(request, alert_id):
    alert = get_object_or_404(CrisisAlert, id=alert_id)
    alert.is_active = not alert.is_active
    alert.save(update_fields=['is_active'])
    return redirect('administration:crisis_alerts')

@user_passes_test(is_admin_check, login_url='/auth/login/')
def admin_settings_view(request):
    success_message = None
    if request.method == 'POST':
        for key, val in request.POST.items():
            if key != 'csrfmiddlewaretoken':
                SystemSetting.objects.update_or_create(
                    setting_key=key,
                    defaults={'setting_value': val}
                )
        success_message = "Platform settings saved successfully."
        
    settings_dict = {}
    for s in SystemSetting.objects.all():
        settings_dict[s.setting_key] = s.setting_value
        
    return render(request, 'administration/admin_settings.html', {
        'settings': settings_dict,
        'success_message': success_message
    })

@user_passes_test(is_admin_check, login_url='/auth/login/')
def admin_logs_view(request):
    logs = UserActivityLog.objects.order_by('-created_at')[:100]
    return render(request, 'administration/admin_logs.html', {'logs': logs})

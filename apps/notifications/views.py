from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.db.models import Q

from .models import Notification, UserReminder

@login_required
def notifications_view(request):
    user = request.user
    notifications = Notification.objects.filter(
        Q(user=user) | Q(is_global=True)
    ).order_by('-created_at')[:40]
    
    reminders = UserReminder.objects.filter(user=user, is_active=True)
    
    return render(request, 'notifications/notifications.html', {
        'notifications': notifications,
        'reminders': reminders,
    })

@login_required
@require_POST
def mark_read_view(request, notif_id):
    notif = get_object_or_404(Notification, id=notif_id)
    if notif.user == request.user or notif.is_global:
        notif.is_read = True
        notif.read_at = timezone.now()
        notif.save(update_fields=['is_read', 'read_at'])
    return redirect('notifications:notifications')

@login_required
@require_POST
def mark_all_read_view(request):
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True, read_at=timezone.now()
    )
    messages.success(request, "All notifications marked as read.")
    return redirect('notifications:notifications')

@login_required
@require_POST
def add_reminder_view(request):
    title = request.POST.get('title', '').strip()
    reminder_type = request.POST.get('reminder_type', 'custom')
    reminder_time = request.POST.get('reminder_time')
    
    if title and reminder_time:
        UserReminder.objects.create(
            user=request.user,
            title=title,
            reminder_type=reminder_type,
            reminder_time=reminder_time,
            is_active=True
        )
        messages.success(request, f"Daily reminder '{title}' saved!")
        
    return redirect('notifications:notifications')

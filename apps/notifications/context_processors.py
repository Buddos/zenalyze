def notifications_context(request):
    if not request.user.is_authenticated:
        return {
            'unread_notifications_count': 0,
            'recent_notifications': [],
            'unread_notifications': 0,
        }

    try:
        from apps.notifications.models import Notification
        from django.db.models import Q
        
        unread_qs = Notification.objects.filter(
            Q(user=request.user) | Q(is_global=True),
            is_read=False
        )
        count = unread_qs.count()
        recent = list(unread_qs.order_by('-created_at')[:5])
        
        return {
            'unread_notifications_count': count,
            'unread_notifications': count,
            'recent_notifications': recent,
        }
    except Exception:
        return {
            'unread_notifications_count': 0,
            'unread_notifications': 0,
            'recent_notifications': [],
        }

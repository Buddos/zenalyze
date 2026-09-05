from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/', views.notifications_view, name='list'),
    path('notifications/<int:notif_id>/read/', views.mark_read_view, name='mark_read'),
    path('notifications/read-all/', views.mark_all_read_view, name='mark_all_read'),
    path('notifications/reminders/add/', views.add_reminder_view, name='add_reminder'),
]

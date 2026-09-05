from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('admin-dashboard/', views.admin_dashboard_view, name='dashboard'),
    path('admin-portal/', views.admin_dashboard_view, name='dashboard_alias'),
    path('admin/users/', views.admin_users_view, name='users'),
    path('admin/users/<int:user_id>/toggle/', views.toggle_user_status_view, name='toggle_user_status'),
    path('admin/moderation/', views.admin_moderation_view, name='moderation'),
    path('admin/moderation/<int:item_id>/<str:action>/', views.review_moderation_view, name='review_moderation'),
    path('admin/crisis-alerts/', views.admin_crisis_alerts_view, name='crisis_alerts'),
    path('admin/crisis-alerts/create/', views.create_crisis_alert_view, name='create_crisis_alert'),
    path('admin/crisis-alerts/<int:alert_id>/toggle/', views.toggle_crisis_alert_view, name='toggle_crisis_alert'),
    path('admin/settings/', views.admin_settings_view, name='settings'),
    path('admin/logs/', views.admin_logs_view, name='logs'),
]

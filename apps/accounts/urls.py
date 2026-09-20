from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('auth/login/', views.login_view, name='login'),
    path('auth/register/', views.register_view, name='register'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/forgot-password/', views.forgot_password_view, name='forgot_password'),
    # Google OAuth2
    path('auth/google/login/', views.google_login_redirect, name='google_login'),
    path('auth/google/callback/', views.google_oauth_callback, name='google_callback'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    path('api/update-theme/', views.update_theme_api, name='update_theme'),
]


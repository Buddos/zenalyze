from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import json

from .models import User, UserSettings, UserActivityLog

def login_view(request):
    if request.user.is_authenticated:
        return redirect('wellness:dashboard')
        
    next_url = request.GET.get('next', 'wellness:dashboard')
    
    if request.method == 'POST':
        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # Identifier can be username or email
        user = None
        if '@' in identifier:
            try:
                user_obj = User.objects.get(email=identifier)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            user = authenticate(request, username=identifier, password=password)
            
        if user is not None:
            if user.is_active:
                login(request, user)
                
                # Log activity
                UserActivityLog.objects.create(
                    user=user,
                    action='login',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
                )
                
                messages.success(request, f"Welcome back, {user.display_title}!")
                return redirect(next_url if next_url.startswith('/') else 'wellness:dashboard')
            else:
                messages.error(request, "This account is currently suspended. Please contact support.")
        else:
            messages.error(request, "Invalid username or password. Please try again.")
            
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('wellness:dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        full_name = request.POST.get('full_name', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if not username or not email or not password:
            messages.error(request, "Please fill in all required fields.")
        elif password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(password) < 6:
            messages.error(request, "Password must be at least 6 characters long.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "This username is already taken.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "An account with this email address already exists.")
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                full_name=full_name,
                role='user'
            )
            UserSettings.objects.create(user=user, theme='light')
            
            # Log in automatically
            login(request, user)
            
            UserActivityLog.objects.create(
                user=user,
                action='register',
                details='New account registered',
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            messages.success(request, "Account created successfully! Welcome to Zenalyze.")
            return redirect('wellness:dashboard')
            
    return render(request, 'accounts/register.html')

def logout_view(request):
    if request.user.is_authenticated:
        UserActivityLog.objects.create(
            user=request.user,
            action='logout',
            ip_address=request.META.get('REMOTE_ADDR')
        )
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect('core:index')

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        messages.success(request, f"If an account exists for {email}, a password reset link has been dispatched.")
        return redirect('accounts:login')
    return render(request, 'accounts/forgot_password.html')

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        user.full_name = request.POST.get('full_name', '').strip()
        user.display_name = request.POST.get('display_name', '').strip()
        user.email = request.POST.get('email', '').strip().lower()
        user.emergency_contact_name = request.POST.get('emergency_contact_name', '').strip()
        user.emergency_contact_phone = request.POST.get('emergency_contact_phone', '').strip()
        
        if 'avatar' in request.FILES:
            user.avatar = request.FILES['avatar']
            
        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('accounts:profile')
        
    return render(request, 'accounts/profile.html', {'user': user})

@login_required
def settings_view(request):
    settings, _ = UserSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        settings.theme = request.POST.get('theme', 'light')
        settings.notifications_enabled = 'notifications_enabled' in request.POST
        settings.email_notifications = 'email_notifications' in request.POST
        settings.save()
        
        request.session['user_theme'] = settings.theme
        messages.success(request, "Your preferences have been saved.")
        return redirect('accounts:settings')
        
    return render(request, 'accounts/settings.html', {'settings': settings})

def update_theme_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            theme = data.get('theme', 'light')
        except Exception:
            theme = request.POST.get('theme', 'light')
            
        if theme not in ['light', 'dark', 'auto']:
            theme = 'light'
            
        request.session['user_theme'] = theme
        
        if request.user.is_authenticated:
            settings, _ = UserSettings.objects.get_or_create(user=request.user)
            settings.theme = theme
            settings.save()
            
        response = JsonResponse({'status': 'success', 'theme': theme})
        response.set_cookie('theme', theme, max_age=365*24*60*60)
        return response
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

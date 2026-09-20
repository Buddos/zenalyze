from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import urllib.request
import urllib.error

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


@csrf_exempt
def google_auth_view(request):
    """Receives a Firebase/Google ID token from the frontend,
    verifies it with Google tokeninfo, then logs the user in
    (creating a Zenalyze account automatically if needed)."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        body = json.loads(request.body)
        id_token = body.get('id_token', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid request body'}, status=400)

    if not id_token:
        return JsonResponse({'status': 'error', 'message': 'No ID token provided'}, status=400)

    # Verify the token with Google tokeninfo endpoint
    try:
        url = f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}'
        with urllib.request.urlopen(url, timeout=10) as resp:
            token_data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return JsonResponse({'status': 'error', 'message': 'Invalid Google token'}, status=401)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Could not verify token'}, status=500)

    google_email = token_data.get('email', '').lower()
    google_name  = token_data.get('name', '')
    google_picture = token_data.get('picture', '')
    email_verified = token_data.get('email_verified', 'false') == 'true'

    if not google_email or not email_verified:
        return JsonResponse({'status': 'error', 'message': 'Email not verified by Google'}, status=401)

    # Get or create the Django user
    created = False
    try:
        user = User.objects.get(email=google_email)
    except User.DoesNotExist:
        # Auto-generate a username from the email prefix
        base_username = google_email.split('@')[0].replace('.', '_')[:30]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=google_email,
            password=None,          # No password — Google-only account
            full_name=google_name,
            role='user',
        )
        if google_picture:
            user.avatar_url = google_picture
        user.save()

        UserSettings.objects.create(user=user, theme='light')
        created = True

    if not user.is_active:
        return JsonResponse({'status': 'error', 'message': 'This account is suspended.'}, status=403)

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    UserActivityLog.objects.create(
        user=user,
        action='google_login' if not created else 'google_register',
        details=f'Signed in via Google ({google_email})',
        ip_address=request.META.get('REMOTE_ADDR'),
    )

    return JsonResponse({
        'status': 'ok',
        'created': created,
        'redirect': '/dashboard/',
    })

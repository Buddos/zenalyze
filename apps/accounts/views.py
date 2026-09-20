from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import urllib.parse
import secrets
import os
import requests as http_requests
from django.conf import settings

from .models import User, UserSettings, UserActivityLog

# Firebase & Google OAuth2 settings
FIREBASE_API_KEY     = getattr(settings, 'FIREBASE_API_KEY', os.environ.get('FIREBASE_API_KEY', 'AIzaSyDwdpQKLtsANsZhPVoqXZ2rjF4tghp-NpQ'))
GOOGLE_CLIENT_ID     = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
GOOGLE_REDIRECT_URI  = os.environ.get('GOOGLE_REDIRECT_URI', 'http://localhost:8000/auth/google/callback/')

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


# ─── Firebase Google Authentication ───────────────────────────────────────────

@csrf_exempt
def google_auth_view(request):
    """Handles Google sign-in and sign-up via Firebase Auth.
    Receives an ID token from the frontend Firebase JavaScript SDK,
    verifies it with Google's Identity Toolkit, and logs the user in."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

    try:
        body = json.loads(request.body)
        id_token = body.get('id_token', '').strip()
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid request body'}, status=400)

    if not id_token:
        return JsonResponse({'status': 'error', 'message': 'No ID token provided'}, status=400)

    google_email = None
    google_name = ''
    google_picture = ''
    email_verified = False

    # 1. Verify token with Firebase Identity Toolkit
    try:
        verify_url = f'https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={FIREBASE_API_KEY}'
        resp = http_requests.post(verify_url, json={'idToken': id_token}, timeout=10)
        resp_data = resp.json()

        if resp.status_code == 200 and 'users' in resp_data and len(resp_data['users']) > 0:
            fb_user = resp_data['users'][0]
            google_email = fb_user.get('email', '').lower().strip()
            google_name = fb_user.get('displayName', '').strip()
            google_picture = fb_user.get('photoUrl', '').strip()
            email_verified = fb_user.get('emailVerified', False)
    except Exception as exc:
        pass

    # 2. Fallback: Google OAuth2 tokeninfo endpoint
    if not google_email:
        try:
            tokeninfo_url = f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}'
            resp = http_requests.get(tokeninfo_url, timeout=10)
            if resp.status_code == 200:
                t_data = resp.json()
                google_email = t_data.get('email', '').lower().strip()
                google_name = t_data.get('name', '').strip()
                google_picture = t_data.get('picture', '').strip()
                email_verified = t_data.get('email_verified', False) in (True, 'true')
        except Exception:
            pass

    if not google_email:
        return JsonResponse({'status': 'error', 'message': 'Could not verify Firebase/Google token'}, status=401)

    # 3. Find or create Django User
    created = False
    try:
        user = User.objects.get(email=google_email)
    except User.DoesNotExist:
        base_username = google_email.split('@')[0].replace('.', '_')[:28]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=google_email,
            password=None,  # Google-only account
            full_name=google_name or username,
            role='user',
        )
        if google_picture:
            user.avatar_url = google_picture
            user.save(update_fields=['avatar_url'])

        UserSettings.objects.get_or_create(user=user, defaults={'theme': 'light'})
        created = True

    if not user.is_active:
        return JsonResponse({'status': 'error', 'message': 'This account is suspended.'}, status=403)

    if google_picture and not user.avatar_url:
        user.avatar_url = google_picture
        user.save(update_fields=['avatar_url'])

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    UserActivityLog.objects.create(
        user=user,
        action='google_register' if created else 'google_login',
        details=f'Firebase Google Sign-In ({google_email})',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
    )

    if created:
        messages.success(request, f"Welcome to Zenalyze, {user.display_title}! Your account has been created via Google.")
    else:
        messages.success(request, f"Welcome back, {user.display_title}!")

    return JsonResponse({
        'status': 'ok',
        'created': created,
        'redirect': '/dashboard/',
    })


# ─── Google OAuth2 (Redirect Flow Fallback) ───────────────────────────────────

def google_login_redirect(request):
    """Step 1: Redirect the user to Google's OAuth2 consent screen."""
    if not GOOGLE_CLIENT_ID:
        messages.error(request, "Google Sign-In is not configured yet. Please ask the admin to add GOOGLE_CLIENT_ID to .env")
        return redirect('accounts:login')

    # Generate a random state token to prevent CSRF
    state = secrets.token_urlsafe(32)
    request.session['google_oauth_state'] = state
    # Remember where to go after login
    next_url = request.GET.get('next', '/dashboard/')
    request.session['google_oauth_next'] = next_url

    params = urllib.parse.urlencode({
        'client_id':     GOOGLE_CLIENT_ID,
        'redirect_uri':  GOOGLE_REDIRECT_URI,
        'response_type': 'code',
        'scope':         'openid email profile',
        'state':         state,
        'access_type':   'online',
        'prompt':        'select_account',
    })
    return redirect(f'https://accounts.google.com/o/oauth2/v2/auth?{params}')


def google_oauth_callback(request):
    """Step 2: Google redirects back here with an authorization code.
    Exchange it for tokens, verify identity, then create/log-in the user."""

    # ── Security: verify state ──────────────────────────────────────────────
    state_in_session = request.session.pop('google_oauth_state', None)
    state_from_google = request.GET.get('state', '')
    if not state_in_session or state_in_session != state_from_google:
        messages.error(request, 'Google sign-in failed: invalid state. Please try again.')
        return redirect('accounts:login')

    error = request.GET.get('error')
    if error:
        if error == 'access_denied':
            messages.info(request, 'Google sign-in was cancelled.')
        else:
            messages.error(request, f'Google sign-in error: {error}')
        return redirect('accounts:login')

    code = request.GET.get('code')
    if not code:
        messages.error(request, 'No authorization code received from Google.')
        return redirect('accounts:login')

    # ── Exchange code for tokens ────────────────────────────────────────────
    try:
        token_resp = http_requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'code':          code,
                'client_id':     GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'redirect_uri':  GOOGLE_REDIRECT_URI,
                'grant_type':    'authorization_code',
            },
            timeout=10
        )
        token_data = token_resp.json()
    except Exception as exc:
        messages.error(request, f'Could not contact Google servers: {exc}')
        return redirect('accounts:login')

    if 'error' in token_data:
        messages.error(request, f'Google token error: {token_data["error_description"]}')
        return redirect('accounts:login')

    access_token = token_data.get('access_token')

    # ── Fetch the user's Google profile ─────────────────────────────────────
    try:
        profile_resp = http_requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        profile = profile_resp.json()
    except Exception as exc:
        messages.error(request, f'Could not fetch Google profile: {exc}')
        return redirect('accounts:login')

    google_email   = profile.get('email', '').lower()
    google_name    = profile.get('name', '')
    google_picture = profile.get('picture', '')
    email_verified = profile.get('verified_email', False)

    if not google_email or not email_verified:
        messages.error(request, 'Google account has no verified email. Please use a different account.')
        return redirect('accounts:login')

    # ── Get or create Django user ────────────────────────────────────────────
    created = False
    try:
        user = User.objects.get(email=google_email)
    except User.DoesNotExist:
        base_username = google_email.split('@')[0].replace('.', '_')[:28]
        username = base_username
        counter  = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=google_email,
            password=None,      # Google-only account, no password
            full_name=google_name,
            role='user',
        )
        if google_picture:
            user.avatar_url = google_picture
        user.save()

        UserSettings.objects.create(user=user, theme='light')
        created = True

    if not user.is_active:
        messages.error(request, 'This account is suspended. Please contact support.')
        return redirect('accounts:login')

    # ── Log in ───────────────────────────────────────────────────────────────
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    UserActivityLog.objects.create(
        user=user,
        action='google_register' if created else 'google_login',
        details=f'Google OAuth sign-in ({google_email})',
        ip_address=request.META.get('REMOTE_ADDR'),
    )

    if created:
        messages.success(request, f'Welcome to Zenalyze, {user.display_title}! Your account was created with Google. 🎉')
    else:
        messages.success(request, f'Welcome back, {user.display_title}!')

    next_url = request.session.pop('google_oauth_next', '/dashboard/')
    return redirect(next_url)


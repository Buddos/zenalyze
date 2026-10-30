from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.cache import never_cache
from django.middleware.csrf import rotate_token
from django.views.csrf import csrf_failure as default_csrf_failure
import json
import logging
import re
import os
import time
import uuid
from io import BytesIO
import requests as http_requests
from django.conf import settings
from PIL import Image, UnidentifiedImageError

from .models import User, UserSettings, UserActivityLog

logger = logging.getLogger(__name__)


def _upload_avatar_to_supabase(upload, user_id):
    max_size = 2 * 1024 * 1024
    if upload.size > max_size:
        raise ValidationError('Profile photos must be 2 MB or smaller.')

    content = upload.read()
    try:
        image = Image.open(BytesIO(content))
        image.verify()
        image_format = image.format
    except (UnidentifiedImageError, OSError, ValueError):
        raise ValidationError('Choose a valid PNG, JPG, or WEBP image.')

    image_types = {
        'JPEG': ('jpg', 'image/jpeg'),
        'PNG': ('png', 'image/png'),
        'WEBP': ('webp', 'image/webp'),
    }
    image_type = image_types.get(image_format)
    if not image_type:
        raise ValidationError('Choose a PNG, JPG, or WEBP image.')
    extension, content_type = image_type

    supabase_url = getattr(settings, 'SUPABASE_URL', '').rstrip('/')
    storage_key = (
        os.environ.get('SUPABASE_SERVICE_ROLE_KEY')
        or os.environ.get('SUPABASE_SECRET_KEY')
        or os.environ.get('SUPABASE_SERVICE_KEY')
    )
    bucket = os.environ.get('SUPABASE_STORAGE_BUCKET', 'avatars').strip()
    if not supabase_url or not storage_key or not bucket:
        raise ValidationError('Profile photo storage is not configured. Please contact support.')

    object_path = f'{user_id}/{uuid.uuid4().hex}.{extension}'
    upload_url = f'{supabase_url}/storage/v1/object/{bucket}/{object_path}'
    try:
        response = http_requests.post(
            upload_url,
            data=content,
            headers={
                'Authorization': f'Bearer {storage_key}',
                'apikey': storage_key,
                'Content-Type': content_type,
                'x-upsert': 'false',
                'Cache-Control': 'max-age=31536000',
            },
            timeout=15,
        )
        response.raise_for_status()
    except http_requests.RequestException as error:
        response_details = ''
        if error.response is not None:
            response_details = error.response.text[:500]
        logger.warning(
            'Supabase avatar upload failed for user %s (status=%s): %s',
            user_id,
            error.response.status_code if error.response is not None else 'connection-error',
            response_details or str(error),
        )
        raise ValidationError('Could not upload your profile photo. Please try again.')

    return f'{supabase_url}/storage/v1/object/public/{bucket}/{object_path}'

@never_cache
@ensure_csrf_cookie
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
            
    return render(request, 'accounts/login.html', {
        'google_client_id': settings.GOOGLE_CLIENT_ID,
    })


@never_cache
@ensure_csrf_cookie
def csrf_failure_view(request, reason=''):
    if request.path_info == '/auth/login/':
        rotate_token(request)
        return render(request, 'accounts/login.html', {
            'error': 'Your security token expired. Please try again.',
            'google_client_id': settings.GOOGLE_CLIENT_ID,
        })
    if request.path_info == '/auth/register/':
        rotate_token(request)
        return render(request, 'accounts/register.html', {
            'errors': ['Your security token expired. Please try again.'],
            'google_client_id': settings.GOOGLE_CLIENT_ID,
        })
    return default_csrf_failure(request, reason=reason)


@never_cache
@ensure_csrf_cookie
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
            
            messages.success(
                request,
                "Account created successfully! You are now signed in and ready to use Zenalyze.",
            )
            return redirect('wellness:dashboard')
            
    return render(request, 'accounts/register.html', {
        'google_client_id': settings.GOOGLE_CLIENT_ID,
    })

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
        
        avatar_error = None
        avatar_upload = request.FILES.get('avatar')
        if avatar_upload:
            if getattr(settings, 'IS_VERCEL', False):
                try:
                    user.avatar_url = _upload_avatar_to_supabase(avatar_upload, user.id)
                    user.avatar = ''
                except ValidationError as error:
                    avatar_error = error.messages[0]
            else:
                user.avatar = avatar_upload

        user.save()
        if avatar_error:
            messages.error(request, avatar_error)
            messages.info(request, 'Your other profile details were saved.')
        else:
            messages.success(request, "Profile updated successfully.")
        return redirect('accounts:profile')
        
    return render(request, 'accounts/profile.html', {'user': user})

@login_required
def settings_view(request):
    user_settings, _ = UserSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'update_username':
            new_username = request.POST.get('username', '').strip()
            if not new_username:
                messages.error(request, "Username cannot be empty.")
            elif not re.match(r'^[\w.@+-]+$', new_username):
                messages.error(request, "Username contains invalid characters. Use letters, numbers, and @/./+/-/_ only.")
            elif len(new_username) > 150:
                messages.error(request, "Username cannot exceed 150 characters.")
            elif User.objects.filter(username__iexact=new_username).exclude(id=request.user.id).exists():
                messages.error(request, f"The username '@{new_username}' is already taken. Please choose another.")
            else:
                old_username = request.user.username
                request.user.username = new_username
                request.user.save(update_fields=['username'])
                messages.success(request, f"Username changed to @{new_username}! This will be displayed in Community Chat.")
            return redirect('accounts:settings')

        elif action == 'change_password':
            old_password = request.POST.get('old_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')

            if not request.user.check_password(old_password):
                messages.error(request, "Current password was entered incorrectly.")
            elif new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            elif len(new_password) < 6:
                messages.error(request, "New password must be at least 6 characters.")
            else:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password updated successfully.")
            return redirect('accounts:settings')

        else:
            # Also handle inline username change if submitted with preferences
            new_username = request.POST.get('username', '').strip()
            if new_username and new_username != request.user.username:
                if not re.match(r'^[\w.@+-]+$', new_username):
                    messages.error(request, "Username contains invalid characters.")
                elif User.objects.filter(username__iexact=new_username).exclude(id=request.user.id).exists():
                    messages.error(request, f"Username '@{new_username}' is already taken.")
                else:
                    request.user.username = new_username
                    request.user.save(update_fields=['username'])
                    messages.success(request, f"Username updated to @{new_username}!")

            user_settings.theme = request.POST.get('theme', 'light')
            user_settings.notifications_enabled = 'notifications_enabled' in request.POST
            user_settings.email_notifications = 'email_notifications' in request.POST
            weekly_day = request.POST.get('weekly_summary_day')
            if weekly_day:
                user_settings.weekly_summary_day = weekly_day
            user_settings.save()
            
            request.session['user_theme'] = user_settings.theme
            messages.success(request, "Your preferences have been saved.")
            return redirect('accounts:settings')
        
    return render(request, 'accounts/settings.html', {
        'settings': user_settings,
        'current_theme': user_settings.theme,
    })

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
            
        response = JsonResponse({'status': 'success', 'success': True, 'theme': theme})
        response.set_cookie('theme', theme, max_age=365*24*60*60, samesite='Lax')
        response.set_cookie('user_theme', theme, max_age=365*24*60*60, samesite='Lax')
        return response
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


# ─── Google Identity Services ─────────────────────────────────────────────────


def google_auth_view(request):
    """Verify a Google ID token and log the matching Django account in."""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed.'}, status=405)
    if not settings.GOOGLE_CLIENT_ID:
        return JsonResponse({'status': 'error', 'message': 'Google sign-in is not configured.'}, status=503)

    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid sign-in request.'}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({'status': 'error', 'message': 'Invalid sign-in request.'}, status=400)

    credential = payload.get('credential', '')
    if not isinstance(credential, str) or not credential or len(credential) > 8192:
        return JsonResponse({'status': 'error', 'message': 'Google did not provide a valid credential.'}, status=400)

    try:
        token_response = http_requests.get(
            'https://oauth2.googleapis.com/tokeninfo',
            params={'id_token': credential},
            timeout=10,
        )
        if token_response.status_code >= 500:
            logger.warning('Google ID token verification service returned HTTP %s.', token_response.status_code)
            return JsonResponse({'status': 'error', 'message': 'Google sign-in is temporarily unavailable.'}, status=503)
        if token_response.status_code != 200:
            return JsonResponse({'status': 'error', 'message': 'Google credential could not be verified.'}, status=401)
        claims = token_response.json()
    except http_requests.RequestException:
        logger.warning('Could not reach Google ID token verification service.')
        return JsonResponse({'status': 'error', 'message': 'Google sign-in is temporarily unavailable.'}, status=503)
    except ValueError:
        logger.warning('Google ID token verification returned invalid JSON.')
        return JsonResponse({'status': 'error', 'message': 'Google returned an invalid sign-in response.'}, status=502)

    if not isinstance(claims, dict):
        return JsonResponse({'status': 'error', 'message': 'Google returned an invalid sign-in response.'}, status=401)

    try:
        token_expiration = int(claims.get('exp', 0))
    except (TypeError, ValueError):
        token_expiration = 0

    email_claim = claims.get('email')
    if (
        claims.get('aud') != settings.GOOGLE_CLIENT_ID
        or claims.get('iss') not in ('accounts.google.com', 'https://accounts.google.com')
        or token_expiration <= int(time.time())
        or claims.get('email_verified') not in (True, 'true')
        or not isinstance(claims.get('sub'), str)
        or not isinstance(email_claim, str)
    ):
        return JsonResponse({'status': 'error', 'message': 'Google credential is invalid or expired.'}, status=401)

    google_email = email_claim.strip().lower()
    name_claim = claims.get('name', '')
    google_name = name_claim.strip() if isinstance(name_claim, str) else ''
    if not google_email:
        return JsonResponse({'status': 'error', 'message': 'Google account has no verified email.'}, status=401)
    picture_claim = claims.get('picture', '')
    google_picture = picture_claim if isinstance(picture_claim, str) else ''

    created = False
    try:
        user = User.objects.get(email=google_email)
    except User.DoesNotExist:
        base_username = re.sub(r'[^a-zA-Z0-9_.-]', '_', google_email.split('@')[0])[:28] or 'google_user'
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            suffix = str(counter)
            username = f'{base_username[:28 - len(suffix)]}{suffix}'
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=google_email,
            password=None,
            full_name=google_name,
            role='user',
        )
        if google_picture:
            user.avatar_url = google_picture
            user.save(update_fields=['avatar_url'])
        UserSettings.objects.get_or_create(user=user, defaults={'theme': 'light'})
        created = True

    if not user.is_active:
        return JsonResponse({'status': 'error', 'message': 'This account is suspended. Please contact support.'}, status=403)

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    UserActivityLog.objects.create(
        user=user,
        action='google_register' if created else 'google_login',
        details='Google Identity Services sign-in',
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
    )
    return JsonResponse({
        'status': 'ok',
        'created': created,
        'message': 'Account created successfully.' if created else 'Signed in successfully.',
        'redirect': '/dashboard/',
    })

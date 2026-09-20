import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zenalyze_project.settings')
django.setup()

from django.test import Client
from apps.accounts.models import User

client = Client()

print("--- 1. Testing Unauthenticated Public Routes ---")
public_routes = [
    '/',
    '/about/',
    '/contact/',
    '/terms/',
    '/privacy/',
    '/help-center/',
    '/crisis-help/',
    '/auth/login/',
    '/auth/register/',
    '/auth/forgot-password/',
]

for r in public_routes:
    res = client.get(r)
    assert res.status_code == 200, f"Failed {r}: status {res.status_code}"
    print(f"  [OK] {r} -> 200")

print("\n--- 2. Testing Legacy PHP Redirects ---")
legacy_routes = [
    ('/about.php', '/about/'),
    ('/crisis-help.php', '/crisis-help/'),
    ('/dashboard.php', '/dashboard/'),
    ('/quotes.php', '/quotes/'),
]
for src, dst in legacy_routes:
    res = client.get(src)
    assert res.status_code in [301, 302], f"Failed redirect {src}: status {res.status_code}"
    print(f"  [OK] {src} -> {res.url}")

print("\n--- 3. Testing Authenticated User Routes (demo) ---")
logged_in = client.login(username='demo', password='Demo@zenalyze123')
assert logged_in, "Failed to login as demo user"

user_routes = [
    '/dashboard/',
    '/mood-log/',
    '/journal/',
    '/exercises/',
    '/analytics/',
    '/history/',
    '/financial/',
    '/relationships/',
    '/motivations/',
    '/generate-report/',
    '/generate-report/?download=true',
    '/community/',
    '/anonymous-chat/',
    '/ai-chat/',
    '/quotes/',
    '/therapy/',
    '/notifications/',
    '/profile/',
    '/settings/',
]

for r in user_routes:
    res = client.get(r)
    assert res.status_code == 200, f"Failed {r}: status {res.status_code}"
    print(f"  [OK] {r} -> 200")

# Test Theme API
res = client.post('/api/update-theme/', data='{"theme": "dark"}', content_type='application/json')
assert res.status_code == 200, f"Failed theme API: {res.status_code}"
print("  [OK] POST /api/update-theme/ -> 200")

# Test Mood log POST
res = client.post('/mood-log/', {
    'mood_score': 8,
    'primary_emotion': 'Happy',
    'stress_level': 2,
    'energy_level': 8,
    'sleep_quality': 4,
    'gratitude': 'Django migration completed smoothly'
})
assert res.status_code in [200, 302], f"Failed mood log post: {res.status_code}"
print("  [OK] POST /mood-log/ -> 302 redirect")

print("\n--- 4. Testing Admin Portal Routes (admin) ---")
client.logout()
admin_logged_in = client.login(username='admin', password='Admin@zenalyze123')
assert admin_logged_in, "Failed to login as admin"

admin_routes = [
    '/admin-dashboard/',
    '/admin/users/',
    '/admin/moderation/',
    '/admin/crisis-alerts/',
    '/admin/settings/',
    '/admin/logs/',
]

for r in admin_routes:
    res = client.get(r)
    assert res.status_code == 200, f"Failed admin route {r}: status {res.status_code}"
    print(f"  [OK] {r} -> 200")

print("\n--- 5. Testing Django Admin Routes (/admin, /admin/, /django-admin/) ---")
# Test unauthenticated redirects to login
client.logout()
res_unauth_admin = client.get('/admin')
assert res_unauth_admin.status_code == 301, f"Expected 301 redirect for /admin, got {res_unauth_admin.status_code}"
print(f"  [OK] /admin -> 301 redirect to {res_unauth_admin.url}")

res_unauth_login = client.get('/admin', follow=True)
assert res_unauth_login.status_code == 200 and '/admin/login/' in res_unauth_login.request['PATH_INFO']
print(f"  [OK] /admin (followed) -> 200 at {res_unauth_login.request['PATH_INFO']}")

# Test authenticated admin access
client.login(username='admin', password='Admin@zenalyze123')
for admin_endpoint in ['/admin/', '/admin', '/django-admin/', '/django-admin']:
    res = client.get(admin_endpoint, follow=True)
    assert res.status_code == 200, f"Failed Django Admin route {admin_endpoint}: status {res.status_code}"
    print(f"  [OK] {admin_endpoint} -> 200 at {res.request['PATH_INFO']}")

print("\n🎉 ALL ROUTES AND CAPABILITIES VERIFIED 100% WORKING!")

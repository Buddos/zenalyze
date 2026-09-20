#!/usr/bin/env python3
"""
Diagnostic utility to check Supabase configuration and PostgreSQL database connection.
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

def check_supabase():
    print("=" * 60)
    print("      Zenalyze -> Supabase Connection Diagnostic")
    print("=" * 60)
    
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_ANON_KEY')
    project_id = os.environ.get('SUPABASE_PROJECT_ID')
    database_url = os.environ.get('DATABASE_URL')
    db_password = os.environ.get('SUPABASE_DB_PASSWORD')
    

    print(f"[*] Supabase URL:        {supabase_url}")
    print(f"[*] Project ID:          {project_id}")
    print(f"[*] Anon/Publishable Key:{' Present' if supabase_key else ' Missing'}")
    print(f"[*] Database URL:        {' Configured' if database_url else ' Not set'}")
    print(f"[*] Supabase DB Password:{' Configured' if db_password else ' Not set'}")
    print("-" * 60)
    
    # 1. Test Supabase REST Reachability
    if supabase_url:
        try:
            import requests
            print("[+] Testing Supabase REST Endpoint reachability...")
            res = requests.get(f"{supabase_url}/rest/v1/", headers={
                'apikey': supabase_key or '',
                'Authorization': f"Bearer {supabase_key or ''}"
            }, timeout=5)
            # Status 200 or 401 (Secret API key required) means the Supabase project is active and responding
            if res.status_code in [200, 401]:
                print(f"    -> Supabase API is REACHABLE and ACTIVE (HTTP status: {res.status_code})")
            else:
                print(f"    -> Supabase returned HTTP status: {res.status_code}")
        except Exception as e:
            print(f"    [!] Error reaching Supabase REST endpoint: {e}")

    # 2. Test PostgreSQL Database Connection
    print("\n[+] Testing Django PostgreSQL Database Connection...")
    if not database_url and not db_password:
        print("    [-] Neither DATABASE_URL nor SUPABASE_DB_PASSWORD is set in .env.")
        print("    [-] Django is currently using the local SQLite fallback: BASE_DIR / 'db.sqlite3'.")
        print("\n--> TO CONNECT TO SUPABASE POSTGRESQL:")
        print("    1. Open your Supabase Dashboard: https://supabase.com/dashboard/project/cpmjwdmjgkqxehjkvhgb")
        print("    2. Navigate to: Project Settings -> Database")
        print("    3. Copy the Connection String (URI) under 'Connection Pooling' (port 6543) or 'Direct' (port 5432).")
        print("    4. Paste it into your .env file as:")
        print("       DATABASE_URL=postgresql://postgres.cpmjwdmjgkqxehjkvhgb:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres")
        print("    5. Run: python manage.py migrate")
        return

    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zenalyze_project.settings')
        django.setup()
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            row = cursor.fetchone()
            print(f"    -> SUCCESS! Connected to PostgreSQL Database:")
            print(f"       {row[0]}")
    except Exception as e:
        print(f"    [!] Database Connection Failed: {e}")
        print("    Please check your database password or host connection pooler settings in .env.")

if __name__ == '__main__':
    check_supabase()

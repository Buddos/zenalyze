# 🧠 Zenalyze — Mental Health & Wellness Platform

<div align="center">

![Zenalyze](https://img.shields.io/badge/Zenalyze-Mental%20Health%20Platform-6C63FF?style=for-the-badge&logo=heart&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.1.1-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)

**A comprehensive mental health and wellness platform designed to help users track moods, journal their thoughts, access guided exercises, connect with therapists, and engage with a supportive community.**

</div>

---

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Supabase Database Setup](#supabase-database-setup)
- [Environment Variables](#environment-variables)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [URL Routes](#url-routes)
- [Database Schema](#database-schema)

---

## 🌟 About the Project

Zenalyze is a full-stack **mental health & wellness platform** built with **Django 6** and backed by **Supabase (PostgreSQL)**. It provides an integrated, secure environment for personal wellness tracking.

### Key Goals
- Reduce stigma around mental health through private, secure journaling
- Surface AI-powered insights from mood patterns and emotional data
- Provide guided wellness exercises (meditation, breathing, yoga, stretching)
- Enable safe, moderated community support and peer connections
- Connect users with verified therapists for professional help

---

## ✨ Features

### 🏠 Personal Dashboard
- Daily wellness score & streak tracking
- Mood trend visualization and analytics
- Personalized motivational quotes and daily tips

### 📊 Mood & Journaling
- **Mood Logging** — Rate mood (1–10), track stress & energy levels, tag emotions
- **Journal Entries** — Private journaling with mood tags, gratitude lists, AI suggestions
- **Mood History** — Calendar and list views of historical mood data
- **Analytics** — Weekly/monthly mood patterns, trigger analysis, emotional trends

### 🧘 Wellness Exercises
- 15+ guided exercises: meditation, breathing, yoga, stretching, mindfulness
- Beginner to advanced difficulty levels
- Step-by-step instructions with benefits tracking
- Session history and completion tracking

### 💬 AI Chat Assistant
- 24/7 AI companion for emotional support
- Sentiment analysis on user messages
- Personalized coping strategy suggestions
- Crisis detection with escalation paths

### 👥 Community
- Anonymous and named community posts
- Categorized discussions (anxiety, depression, self-care, relationships, mindfulness)
- Post likes, comments, and moderation system
- Anonymous peer chat sessions

### 🏥 Therapy
- Verified therapist directory with profiles
- Session booking and scheduling
- Review and rating system
- Therapy resource library

### 💰 Financial Wellness
- Income and expense tracking
- Financial goal setting with mood correlation
- Spending pattern insights

### 🛡️ Administration
- Full admin portal with user management
- Content moderation dashboard
- Crisis alert management
- System settings control panel
- Audit logs for all administrative actions

---

## 🛠 Tech Stack

| Layer | Technology |
|:---|:---|
| **Backend Framework** | Django 6.1.1 (Python 3.14) |
| **Primary Database** | Supabase (PostgreSQL 15+) |
| **Local Dev DB** | SQLite (automatic fallback) |
| **ORM** | Django ORM |
| **Authentication** | Django Auth + Custom User Model |
| **Image Processing** | Pillow 12.3.0 |
| **DB Driver** | psycopg2-binary |
| **Environment Config** | python-dotenv |
| **DB URL Parsing** | dj-database-url |
| **Frontend** | HTML5, Vanilla CSS, JavaScript |
| **Icons** | Bootstrap Icons |

---

## 📦 Prerequisites

- **Python** 3.10+ (project uses 3.14)
- **pip** 20+
- **Git**
- A **Supabase** account at [supabase.com](https://supabase.com) (free tier works)

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/your-username/zenalyze.git
cd zenalyze
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Create a superuser

```bash
python manage.py createsuperuser
```

### 7. Seed initial data

```bash
python manage.py seed_from_legacy
```

### 8. Start the development server

```bash
python manage.py runserver
```

Visit **http://localhost:8000** 🎉

---

## 🗄 Supabase Database Setup

The project ships with a ready-to-run PostgreSQL migration file for Supabase.

### Steps

1. **Create a Supabase project** at [supabase.com/dashboard](https://supabase.com/dashboard)

2. **Open the SQL Editor**:
   Navigate to your project → **SQL Editor** → **New Query**

3. **Run the migration**:
   Copy the contents of `supabase_schema_and_data.sql` and paste into the editor, then click **Run**.

   > This creates all **49 tables** with proper indexes, constraints, sequences, and seed data.

4. **Get your connection string**:
   Go to **Project Settings → Database → Connection String (URI)**
   Copy the **Transaction Pooler** URI (port `6543`).

5. **Add to `.env`**:
   ```env
   DATABASE_URL=postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
   ```

6. **Apply Django migrations**:
   ```bash
   python manage.py migrate
   ```

### Verify the connection

```bash
python check_supabase_connection.py
```

---

## ⚙️ Environment Variables

Create a `.env` file in the project root (use `.env.example` as a template):

```env
# Django
DJANGO_SECRET_KEY=your-long-secret-key-here
DEBUG=True

# Supabase Project Info
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-publishable-key
SUPABASE_PROJECT_ID=your-project-id

# Database — uncomment and fill in your password to connect to Supabase
# DATABASE_URL=postgresql://postgres.[project-id]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres

# If DATABASE_URL is not set, SQLite is used automatically for local development
```

> **Note:** If `DATABASE_URL` is not configured, the app automatically falls back to a local SQLite database (`db.sqlite3`). No Supabase config needed for local development.

### Vercel deployment

Add `DATABASE_URL` to the Vercel project's Environment Variables for every deployment environment, using the Supabase PostgreSQL Transaction Pooler URI. Vercel deployments intentionally fail during startup if PostgreSQL is not configured; they must not fall back to ephemeral SQLite storage. Django user accounts, login activity, and database-backed authentication sessions are stored in that PostgreSQL database.

After configuring the database, apply Django migrations to the Supabase database:

```bash
python manage.py migrate
```

Do not put the database password in source control or paste it into chat or command text. If a database credential is exposed, rotate it in Supabase and update the Vercel `DATABASE_URL` immediately.

---

## ▶️ Running the Application

```bash
# Development server
python manage.py runserver

# Verify all routes are working
python verify_all_routes.py

# Check Supabase connection status
python check_supabase_connection.py

# Seed exercises, system settings, motivations, and notifications
python manage.py seed_from_legacy

# Run Django checks
python manage.py check
```

---

## 📁 Project Structure

```
zenalyze/
├── apps/
│   ├── accounts/           # User model, auth, settings, activity logs
│   ├── administration/     # Admin portal, system settings, crisis management
│   ├── community/          # Posts, comments, likes, anonymous chat
│   ├── core/               # Landing, about, contact, context processors
│   │   └── management/
│   │       └── commands/
│   │           └── seed_from_legacy.py   # Seeds legacy data into Django
│   ├── notifications/      # Notifications, reminders, announcements
│   ├── quotes/             # Quote library, daily quotes, interactions
│   ├── therapists/         # Therapist directory, sessions, reviews
│   └── wellness/           # Mood, journal, exercises, financial, relationships
│
├── templates/              # Django HTML templates
├── static/                 # CSS, JavaScript, images
├── media/                  # User-uploaded files (avatars, etc.)
│
├── zenalyze_project/
│   ├── settings.py         # Django settings (Supabase + SQLite config)
│   ├── urls.py             # Root URL configuration
│   └── wsgi.py
│
├── supabase_schema_and_data.sql    # Full PostgreSQL schema for Supabase (49 tables)
├── check_supabase_connection.py   # Connection diagnostic tool
├── verify_all_routes.py           # Full route test suite
├── .env                           # Environment variables (not committed)
├── .env.example                   # Template for environment variables
├── requirements.txt               # Python dependencies
├── manage.py
└── README.md
```

---

## 🔗 URL Routes

| Route | Description | Auth Required |
|:---|:---|:---:|
| `/` | Landing page | No |
| `/about/` | About page | No |
| `/crisis-help/` | Crisis resources | No |
| `/auth/login/` | Login | No |
| `/auth/register/` | Registration | No |
| `/dashboard/` | User dashboard | Yes |
| `/mood-log/` | Log mood entry | Yes |
| `/journal/` | Journal entries | Yes |
| `/exercises/` | Wellness exercises | Yes |
| `/analytics/` | Mood analytics | Yes |
| `/history/` | Wellness history | Yes |
| `/financial/` | Financial tracker | Yes |
| `/relationships/` | Relationship tracking | Yes |
| `/motivations/` | Daily motivations | Yes |
| `/community/` | Community posts | Yes |
| `/anonymous-chat/` | Anonymous chat | Yes |
| `/ai-chat/` | AI companion chat | Yes |
| `/quotes/` | Daily quotes | Yes |
| `/therapy/` | Therapist directory | Yes |
| `/notifications/` | Notifications | Yes |
| `/profile/` | User profile | Yes |
| `/settings/` | Account settings | Yes |
| `/admin-dashboard/` | Admin portal | Admin |
| `/admin/users/` | User management | Admin |
| `/admin/moderation/` | Content moderation | Admin |
| `/admin/crisis-alerts/` | Crisis management | Admin |
| `/admin/settings/` | System settings | Admin |
| `/admin/logs/` | Admin audit logs | Admin |

---

## 🗃 Database Schema

The database consists of **49 tables** across functional groups:

| Group | Tables |
|:---|:---|
| **Users & Auth** | `users`, `admin_users`, `user_settings`, `sessions`, `session_tracking`, `remember_tokens`, `user_activity_log` |
| **Mood & Wellness** | `mood_entries`, `exercises`, `coping_strategies`, `stress_patterns`, `daily_insights`, `relaxation_sessions` |
| **Motivation** | `daily_motivations` |
| **Quotes & Audio** | `quotes`, `daily_quotes`, `quote_user_interactions`, `audio_library` |
| **Community** | `community_posts`, `post_categories`, `post_comments`, `community_comments`, `post_likes`, `community_messages` |
| **Anonymous Features** | `anonymous_entries`, `anonymous_chat_sessions`, `anonymous_messages` |
| **AI & Chat** | `ai_chat_sessions`, `ai_chat_messages`, `ai_analysis_logs`, `chat_sessions`, `chat_messages` |
| **Therapy** | `therapists`, `therapist_sessions`, `therapy_sessions`, `therapist_reviews`, `relationship_entries` |
| **Financial** | `financial_entries`, `financial_goals` |
| **Crisis & Safety** | `crisis_alerts`, `crisis_resources`, `content_moderation` |
| **Administration** | `admin_logs`, `system_settings`, `system_notifications`, `notification_settings`, `user_notifications`, `articles`, `user_coping_history` |

Full schema with CREATE TABLE statements available in [`supabase_schema_and_data.sql`](./supabase_schema_and_data.sql).

---

## 🔐 Security

- Passwords hashed with Django's PBKDF2 + SHA-256
- CSRF protection on all state-changing views
- 30-minute session timeout on inactivity
- All credentials stored in environment variables — never in source code
- Row-Level Security (RLS) can be enabled on Supabase tables for extra protection

---

## 📄 License

Distributed under the MIT License.

---

## 📬 Contact

**Bonface Mwongera** — [bonifacemwongera02@gmail.com](mailto:bonifacemwongera02@gmail.com)

---

<div align="center">
Made with ❤️ for mental health awareness
</div>

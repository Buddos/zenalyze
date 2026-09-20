-- =============================================================================
-- Supabase / PostgreSQL Schema and Data Migration for Zenalyze Platform
-- Generated from legacy MySQL dump
-- Compatible with Supabase SQL Editor
-- =============================================================================

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- -----------------------------------------------------------------------------
-- 1. admin_logs
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS admin_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER DEFAULT NULL,
    action VARCHAR(255) NOT NULL,
    details TEXT DEFAULT NULL,
    ip_address VARCHAR(45) DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_admin_logs_admin_id ON admin_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_admin_logs_created_at ON admin_logs(created_at);

INSERT INTO admin_logs (id, admin_id, action, details, ip_address, created_at) VALUES
(1, NULL, 'System Setup', 'Admin logs table created', '127.0.0.1', '2026-02-27 19:24:06+00'),
(2, NULL, 'System Initialized', 'Admin logs table created successfully', '127.0.0.1', '2026-02-27 19:24:28+00')
ON CONFLICT (id) DO NOTHING;

SELECT setval(pg_get_serial_sequence('admin_logs', 'id'), COALESCE((SELECT MAX(id) FROM admin_logs), 1));

-- -----------------------------------------------------------------------------
-- 2. admin_users
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) DEFAULT NULL,
    role VARCHAR(20) DEFAULT 'admin' CHECK (role IN ('super_admin','admin','moderator')),
    last_login TIMESTAMPTZ DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO admin_users (id, username, email, password_hash, full_name, role, last_login, created_at, updated_at) VALUES
(3, 'dashing', 'dashing@admin.com', '$2y$10$1VRHfv//jQwN1E93wew4yunSqYAuROHcDecGrARl3x5zjbkAqa1d.', 'Dashing Admin', 'super_admin', '2026-02-27 06:15:24+00', '2026-02-26 15:10:21+00', '2026-02-27 06:15:24+00'),
(4, 'admin', 'admin@zenalyze.com', '$2y$10$YourHashedPasswordHere', 'Administrator', 'super_admin', NULL, '2026-02-27 07:12:18+00', '2026-02-27 07:12:18+00')
ON CONFLICT (id) DO NOTHING;

SELECT setval(pg_get_serial_sequence('admin_users', 'id'), COALESCE((SELECT MAX(id) FROM admin_users), 1));

-- -----------------------------------------------------------------------------
-- 3. ai_analysis_logs
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_analysis_logs (
    id SERIAL PRIMARY KEY,
    entry_id INTEGER NOT NULL,
    entry_type VARCHAR(20) DEFAULT 'mood',
    ai_model VARCHAR(50) DEFAULT 'gpt-3.5',
    analysis_type VARCHAR(20) DEFAULT 'sentiment',
    detected_emotions TEXT DEFAULT NULL,
    sentiment_score DECIMAL(3,2) DEFAULT NULL,
    risk_level VARCHAR(20) DEFAULT 'low',
    key_phrases TEXT DEFAULT NULL,
    themes TEXT DEFAULT NULL,
    recommendations TEXT DEFAULT NULL,
    processed_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    processing_time_ms INTEGER DEFAULT NULL
);

-- -----------------------------------------------------------------------------
-- 4. ai_chat_messages
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    sender_type VARCHAR(10) DEFAULT 'user',
    message_text TEXT NOT NULL,
    sentiment_score DECIMAL(3,2) DEFAULT NULL,
    detected_emotions TEXT DEFAULT NULL,
    suggestions_generated TEXT DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 5. ai_chat_sessions
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ai_chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_name VARCHAR(100) DEFAULT NULL,
    initial_mood INTEGER DEFAULT NULL
);

-- -----------------------------------------------------------------------------
-- 6. anonymous_chat_sessions
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS anonymous_chat_sessions (
    id SERIAL PRIMARY KEY,
    session_code VARCHAR(50) NOT NULL UNIQUE,
    participant1_id INTEGER NOT NULL,
    participant2_id INTEGER DEFAULT NULL,
    status VARCHAR(20) DEFAULT 'waiting',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMPTZ DEFAULT NULL
);
CREATE INDEX IF NOT EXISTS idx_anon_chat_status ON anonymous_chat_sessions(status);

-- -----------------------------------------------------------------------------
-- 7. anonymous_entries
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS anonymous_entries (
    id SERIAL PRIMARY KEY,
    anonymous_id VARCHAR(50) NOT NULL,
    content_type VARCHAR(20) DEFAULT 'thought',
    content TEXT NOT NULL,
    emotions TEXT DEFAULT NULL,
    intensity_level INTEGER DEFAULT 5,
    context_tags TEXT DEFAULT NULL,
    ai_analysis TEXT DEFAULT NULL,
    ai_response TEXT DEFAULT NULL,
    ai_suggestions TEXT DEFAULT NULL,
    ai_coping_strategies TEXT DEFAULT NULL,
    emergency_flag BOOLEAN DEFAULT FALSE,
    community_visible BOOLEAN DEFAULT FALSE,
    response_needed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMPTZ DEFAULT (CURRENT_TIMESTAMP + INTERVAL '30 day')
);

-- -----------------------------------------------------------------------------
-- 8. anonymous_messages
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS anonymous_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    message_text TEXT NOT NULL,
    is_anonymous SMALLINT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_anon_msgs_session_id ON anonymous_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_anon_msgs_created_at ON anonymous_messages(created_at);

-- -----------------------------------------------------------------------------
-- 9. articles
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS articles (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL UNIQUE,
    excerpt TEXT DEFAULT NULL,
    content TEXT NOT NULL,
    featured_image VARCHAR(255) DEFAULT NULL,
    category VARCHAR(50) DEFAULT NULL,
    tags TEXT DEFAULT NULL,
    author_id INTEGER DEFAULT NULL,
    view_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    is_published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMPTZ DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles(is_published);
CREATE INDEX IF NOT EXISTS idx_articles_author ON articles(author_id);

-- -----------------------------------------------------------------------------
-- 10. audio_library
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS audio_library (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT DEFAULT NULL,
    category VARCHAR(50) DEFAULT 'meditation',
    audio_url TEXT NOT NULL,
    duration_seconds INTEGER DEFAULT NULL,
    mood_target TEXT DEFAULT NULL,
    favorite_count INTEGER DEFAULT 0,
    play_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 11. chat_messages
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chat_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    sender_type VARCHAR(10) DEFAULT 'user',
    message_text TEXT NOT NULL,
    sentiment_score DECIMAL(3,2) DEFAULT NULL,
    detected_emotions TEXT DEFAULT NULL,
    suggestions_generated TEXT DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 12. chat_sessions
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chat_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_name VARCHAR(100) DEFAULT NULL,
    initial_mood INTEGER DEFAULT NULL,
    final_mood INTEGER DEFAULT NULL,
    topic VARCHAR(100) DEFAULT NULL,
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_message_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 13. community_comments
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS community_comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    parent_comment_id INTEGER DEFAULT NULL,
    content TEXT NOT NULL,
    is_anonymous BOOLEAN DEFAULT FALSE,
    likes_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 14. community_messages
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS community_messages (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    is_anonymous SMALLINT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_comm_msgs_user_id ON community_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_comm_msgs_created_at ON community_messages(created_at);

-- -----------------------------------------------------------------------------
-- 15. community_posts
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS community_posts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) DEFAULT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'support',
    mood_tag VARCHAR(50) DEFAULT NULL,
    is_anonymous BOOLEAN DEFAULT FALSE,
    likes_count INTEGER DEFAULT 0,
    comments_count INTEGER DEFAULT 0,
    privacy_level VARCHAR(20) DEFAULT 'public',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    view_count INTEGER DEFAULT 0
);

-- -----------------------------------------------------------------------------
-- 16. content_moderation
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS content_moderation (
    id SERIAL PRIMARY KEY,
    content_type VARCHAR(30) NOT NULL,
    content_id INTEGER NOT NULL,
    reported_by INTEGER DEFAULT NULL,
    reason VARCHAR(255) DEFAULT NULL,
    description TEXT DEFAULT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    moderator_notes TEXT DEFAULT NULL,
    moderated_by INTEGER DEFAULT NULL,
    moderated_at TIMESTAMPTZ DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_content_mod_reported ON content_moderation(reported_by);
CREATE INDEX IF NOT EXISTS idx_content_mod_moderated ON content_moderation(moderated_by);

-- -----------------------------------------------------------------------------
-- 17. coping_strategies
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS coping_strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT NULL,
    strategy_type VARCHAR(50) DEFAULT 'mindfulness',
    intensity_level VARCHAR(20) DEFAULT 'moderate',
    target_emotions TEXT DEFAULT NULL,
    duration_minutes INTEGER DEFAULT 5,
    steps TEXT DEFAULT NULL,
    effectiveness_rating DECIMAL(3,2) DEFAULT 3.50,
    ai_generated BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 18. crisis_alerts
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crisis_alerts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    affected_users TEXT DEFAULT NULL,
    is_active SMALLINT DEFAULT 1,
    expires_at TIMESTAMPTZ DEFAULT NULL,
    created_by INTEGER DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_crisis_alerts_created_by ON crisis_alerts(created_by);

-- -----------------------------------------------------------------------------
-- 19. crisis_resources
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS crisis_resources (
    id SERIAL PRIMARY KEY,
    resource_name VARCHAR(100) NOT NULL,
    resource_type VARCHAR(20) DEFAULT 'helpline',
    country VARCHAR(50) DEFAULT NULL,
    phone_number VARCHAR(20) DEFAULT NULL,
    website_url TEXT DEFAULT NULL,
    description TEXT DEFAULT NULL,
    languages TEXT DEFAULT NULL,
    available_24_7 BOOLEAN DEFAULT TRUE,
    priority_level INTEGER DEFAULT 1
);

-- -----------------------------------------------------------------------------
-- 20. daily_insights
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_insights (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    insight_type VARCHAR(30) DEFAULT 'suggestion',
    insight_text TEXT NOT NULL,
    data_source TEXT DEFAULT NULL,
    relevance_score DECIMAL(3,2) DEFAULT 1.00
);

-- -----------------------------------------------------------------------------
-- 21. daily_motivations
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_motivations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    motivation_text TEXT NOT NULL,
    motivation_type VARCHAR(50) NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMPTZ DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO daily_motivations (id, user_id, motivation_text, motivation_type, is_completed, completed_at, created_at) VALUES
(1, 4, 'Small steps every day lead to big changes. Be patient with yourself.', 'tip', FALSE, NULL, '2026-02-22 19:55:14+00'),
(2, 12, 'Take a deep breath. You are exactly where you need to be right now.', 'affirmation', TRUE, '2026-02-23 20:06:45+00', '2026-02-23 20:06:36+00'),
(3, 12, 'You are stronger than you think, more capable than you know, and loved more than you can imagine.', 'affirmation', TRUE, '2026-02-24 04:32:01+00', '2026-02-24 04:31:49+00')
ON CONFLICT (id) DO NOTHING;

SELECT setval(pg_get_serial_sequence('daily_motivations', 'id'), COALESCE((SELECT MAX(id) FROM daily_motivations), 1));

-- -----------------------------------------------------------------------------
-- 22. daily_quotes
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_quotes (
    id SERIAL PRIMARY KEY,
    quote_text TEXT NOT NULL,
    author VARCHAR(100) DEFAULT NULL,
    category VARCHAR(50) DEFAULT 'motivational',
    mood_target TEXT DEFAULT NULL,
    popularity_score INTEGER DEFAULT 0,
    ai_generated BOOLEAN DEFAULT FALSE,
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------------------------------------
-- 23. exercises
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS exercises (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    description TEXT DEFAULT NULL,
    category VARCHAR(50) DEFAULT 'mindfulness',
    duration_minutes INTEGER DEFAULT 10,
    difficulty VARCHAR(20) DEFAULT 'beginner',
    video_url TEXT DEFAULT NULL,
    audio_url TEXT DEFAULT NULL,
    steps TEXT DEFAULT NULL,
    benefits TEXT DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

INSERT INTO exercises (id, title, description, category, duration_minutes, difficulty, video_url, audio_url, steps, benefits, created_at, is_active) VALUES
(1, 'Basic Mindfulness Meditation', 'A simple meditation to center your thoughts and find calm.', 'meditation', 5, 'beginner', NULL, NULL, '1. Find a quiet space
2. Sit comfortably
3. Focus on your breath
4. When your mind wanders, gently bring it back
5. Continue for 5 minutes', 'Reduces stress, Improves focus, Increases self-awareness', '2026-02-23 19:58:05+00', TRUE),
(2, 'Deep Breathing Exercise', 'Calm your nervous system with deep, controlled breathing.', 'breathing', 3, 'beginner', NULL, NULL, '1. Find a comfortable seated position
2. Inhale deeply through your nose for 4 counts
3. Hold your breath for 4 counts
4. Exhale slowly through your mouth for 6 counts
5. Repeat for 3 minutes', 'Reduces anxiety, Lowers blood pressure, Improves lung function', '2026-02-23 19:58:05+00', TRUE),
(3, 'Morning Yoga Flow', 'Gentle yoga poses to energize your morning.', 'yoga', 10, 'beginner', NULL, NULL, '1. Mountain pose (Tadasana) - 1 min
2. Upward salute (Urdhva Hastasana) - 1 min
3. Forward fold (Uttanasana) - 1 min
4. Plank pose - 1 min
5. Cobra pose (Bhujangasana) - 1 min
6. Downward dog (Adho Mukha Svanasana) - 2 min
7. Repeat sequence', 'Increases energy, Improves flexibility, Boosts mood', '2026-02-23 19:58:05+00', TRUE),
(4, 'Body Scan Meditation', 'Bring awareness to each part of your body.', 'meditation', 10, 'intermediate', NULL, NULL, '1. Lie down comfortably
2. Bring attention to your feet
3. Slowly move awareness up through legs
4. Scan through torso
5. Move to arms and hands
6. Scan neck and head
7. Notice your whole body', 'Reduces tension, Improves body awareness, Promotes relaxation', '2026-02-23 19:58:05+00', TRUE),
(5, '4-7-8 Breathing', 'A powerful breathing technique for relaxation.', 'breathing', 4, 'beginner', NULL, NULL, '1. Inhale quietly through nose for 4 seconds
2. Hold breath for 7 seconds
3. Exhale completely through mouth for 8 seconds
4. Repeat 4 times', 'Calms nervous system, Reduces anxiety, Helps with sleep', '2026-02-23 19:58:05+00', TRUE),
(6, 'Stress Relief Yoga', 'Yoga poses specifically for stress relief.', 'yoga', 10, 'beginner', NULL, NULL, '1. Child pose (Balasana) - 2 min
2. Cat-cow stretch (Marjaryasana-Bitilasana) - 2 min
3. Downward dog (Adho Mukha Svanasana) - 2 min
4. Forward fold (Uttanasana) - 2 min
5. Legs-up-the-wall (Viparita Karani) - 2 min', 'Reduces stress hormones, Relaxes mind, Releases tension', '2026-02-23 19:58:05+00', TRUE),
(7, '5 Senses Mindfulness', 'Ground yourself by engaging all five senses.', 'mindfulness', 5, 'beginner', NULL, NULL, '1. Notice 5 things you can see
2. Notice 4 things you can touch
3. Notice 3 things you can hear
4. Notice 2 things you can smell
5. Notice 1 thing you can taste', 'Reduces anxiety, Increases present-moment awareness, Grounding technique', '2026-02-23 19:58:05+00', TRUE),
(8, 'Loving-Kindness Meditation', 'Cultivate compassion for yourself and others.', 'meditation', 10, 'intermediate', NULL, NULL, '1. Sit comfortably
2. Bring to mind someone you love
3. Silently repeat: "May you be happy. May you be healthy. May you be safe."
4. Extend these wishes to yourself
5. Extend to all beings everywhere', 'Increases compassion, Reduces negative emotions, Improves relationships', '2026-02-23 19:58:05+00', TRUE),
(9, 'Alternate Nostril Breathing', 'Balance your energy with this breathing technique.', 'breathing', 5, 'intermediate', NULL, NULL, '1. Close right nostril with thumb
2. Inhale through left nostril
3. Close left nostril with ring finger
4. Release right nostril and exhale
5. Inhale through right nostril
6. Close right nostril
7. Release left and exhale
8. Repeat cycle', 'Balances brain hemispheres, Calms mind, Improves focus', '2026-02-23 19:58:05+00', TRUE),
(10, 'Sun Salutation', 'Classic yoga flow to energize the body.', 'yoga', 15, 'intermediate', NULL, NULL, '1. Mountain pose
2. Raise arms (upward salute)
3. Forward fold
4. Half lift
5. Plank pose
6. Chaturanga
7. Upward dog
8. Downward dog
9. Forward fold
10. Raise arms
11. Mountain pose', 'Full body workout, Improves circulation, Builds strength', '2026-02-23 19:58:05+00', TRUE),
(11, 'Walking Meditation', 'Practice mindfulness while walking.', 'mindfulness', 10, 'beginner', NULL, NULL, '1. Walk slowly and naturally
2. Focus on sensation of feet touching ground
3. Notice each step
4. Be aware of your surroundings
5. When mind wanders, gently bring attention back to walking', 'Combines exercise with mindfulness, Reduces stress, Improves focus', '2026-02-23 19:58:05+00', TRUE),
(12, 'Gratitude Meditation', 'Cultivate feelings of gratitude.', 'meditation', 8, 'beginner', NULL, NULL, '1. Sit comfortably
2. Think of three things you''re grateful for
3. Hold each in your mind for a minute
4. Feel the warmth of gratitude in your heart
5. Send gratitude outward', 'Increases happiness, Improves mood, Shifts mindset to positivity', '2026-02-23 19:58:05+00', TRUE),
(13, 'Neck and Shoulder Stretch', 'Release tension in neck and shoulders.', 'stretching', 5, 'beginner', NULL, NULL, '1. Sit up straight
2. Slowly tilt head to right shoulder
3. Hold for 30 seconds
4. Repeat on left side
5. Roll shoulders forward 10 times
6. Roll shoulders backward 10 times
7. Interlace hands behind back and straighten arms', 'Releases tension, Improves posture, Reduces headaches', '2026-02-23 19:58:05+00', TRUE),
(14, 'Full Body Stretching', 'Complete stretching routine for whole body.', 'stretching', 12, 'intermediate', NULL, NULL, '1. Neck rolls - 1 min
2. Shoulder stretches - 2 min
3. Chest opener - 1 min
4. Tricep stretches - 1 min
5. Seated forward fold - 2 min
6. Butterfly stretch - 2 min
7. Quadriceps stretch - 2 min
8. Calf stretches - 1 min', 'Improves flexibility, Prevents injury, Increases blood flow', '2026-02-23 19:58:05+00', TRUE),
(15, 'Box Breathing', 'Simple breathing technique for focus and calm.', 'breathing', 3, 'beginner', NULL, NULL, '1. Inhale through nose for 4 counts
2. Hold breath for 4 counts
3. Exhale through mouth for 4 counts
4. Hold empty lungs for 4 counts
5. Repeat', 'Reduces stress, Improves focus, Calms nervous system', '2026-02-23 19:58:05+00', TRUE)
ON CONFLICT (id) DO NOTHING;

SELECT setval(pg_get_serial_sequence('exercises', 'id'), COALESCE((SELECT MAX(id) FROM exercises), 1));

-- --------------------------------------------------------
-- 24. financial_entries
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS financial_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    category VARCHAR(20) DEFAULT 'expense',
    subcategory VARCHAR(50) DEFAULT NULL,
    description TEXT DEFAULT NULL,
    payment_method VARCHAR(50) DEFAULT NULL,
    mood_before INTEGER DEFAULT NULL
);

-- --------------------------------------------------------
-- 25. financial_goals
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS financial_goals (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    goal_name VARCHAR(100) NOT NULL,
    target_amount DECIMAL(10,2) NOT NULL,
    current_amount DECIMAL(10,2) DEFAULT 0.00,
    deadline DATE DEFAULT NULL,
    category VARCHAR(50) DEFAULT 'other',
    priority VARCHAR(20) DEFAULT 'medium',
    mood_impact TEXT DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    target_date DATE DEFAULT NULL,
    currency VARCHAR(3) DEFAULT 'USD'
);

-- --------------------------------------------------------
-- 26. mood_entries
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS mood_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    mood_score INTEGER NOT NULL,
    stress_level INTEGER DEFAULT NULL,
    energy_level INTEGER DEFAULT NULL,
    journal_entry TEXT DEFAULT NULL,
    primary_emotion VARCHAR(50) DEFAULT NULL,
    secondary_emotions TEXT DEFAULT NULL,
    tags TEXT DEFAULT NULL,
    triggers TEXT DEFAULT NULL,
    location VARCHAR(100) DEFAULT NULL,
    weather VARCHAR(50) DEFAULT NULL,
    social_context VARCHAR(50) DEFAULT NULL,
    physical_symptoms TEXT DEFAULT NULL,
    ai_analysis TEXT DEFAULT NULL,
    ai_suggestions TEXT DEFAULT NULL,
    privacy_level VARCHAR(20) DEFAULT 'private',
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    entry_date DATE DEFAULT CURRENT_DATE
);

-- --------------------------------------------------------
-- 27. notification_settings
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS notification_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    email_notifications SMALLINT DEFAULT 1,
    push_notifications SMALLINT DEFAULT 1,
    quote_notifications SMALLINT DEFAULT 1,
    mood_reminder SMALLINT DEFAULT 1,
    insight_notifications SMALLINT DEFAULT 1,
    community_notifications SMALLINT DEFAULT 1,
    friend_notifications SMALLINT DEFAULT 1,
    emergency_alerts SMALLINT DEFAULT 1,
    quiet_hours_start TIME DEFAULT '22:00:00',
    quiet_hours_end TIME DEFAULT '08:00:00',
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO notification_settings (id, user_id, email_notifications, push_notifications, quote_notifications, mood_reminder, insight_notifications, community_notifications, friend_notifications, emergency_alerts, quiet_hours_start, quiet_hours_end, updated_at) VALUES
(4, 11, 1, 1, 1, 1, 1, 1, 1, 1, '22:00:00', '08:00:00', '2026-03-28 13:16:52+00'),
(5, 12, 1, 1, 1, 1, 1, 1, 1, 1, '22:00:00', '08:00:00', '2026-03-28 13:16:52+00')
ON CONFLICT (user_id) DO NOTHING;

SELECT setval(pg_get_serial_sequence('notification_settings', 'id'), COALESCE((SELECT MAX(id) FROM notification_settings), 1));

-- --------------------------------------------------------
-- 28. post_categories
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS post_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT DEFAULT NULL,
    icon VARCHAR(50) DEFAULT NULL,
    color VARCHAR(20) DEFAULT NULL,
    post_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO post_categories (id, name, description, icon, color, post_count, is_active, created_at) VALUES
(1, 'General Support', 'General mental health discussions and support', 'people', '#5D8AA8', 0, TRUE, '2026-02-21 16:52:15+00'),
(2, 'Anxiety', 'Discuss anxiety, fears, and coping strategies', 'brain', '#7FB685', 0, TRUE, '2026-02-21 16:52:15+00'),
(3, 'Depression', 'Support for depression and mood disorders', 'cloud', '#B8B8D1', 0, TRUE, '2026-02-21 16:52:15+00'),
(4, 'Relationships', 'Relationship advice and experiences', 'heart', '#E6B89C', 0, TRUE, '2026-02-21 16:52:15+00'),
(5, 'Self-Care', 'Self-care tips, routines, and practices', 'flower1', '#9CAFB7', 0, TRUE, '2026-02-21 16:52:15+00'),
(6, 'Success Stories', 'Share your wins and progress', 'star', '#F4B886', 0, TRUE, '2026-02-21 16:52:15+00'),
(7, 'Resources', 'Share helpful resources and tools', 'book', '#ADB9C3', 0, TRUE, '2026-02-21 16:52:15+00'),
(8, 'Mindfulness', 'Practices for present moment awareness', 'flower2', '#5E9B9D', 0, TRUE, '2026-02-28 03:21:45+00'),
(9, 'Growth', 'Personal development and growth', 'arrow-up-circle', '#F2C94C', 0, TRUE, '2026-02-28 03:21:45+00'),
(10, 'Community Questions', 'Ask questions and seek advice', 'question-circle', '#9F86C0', 0, TRUE, '2026-03-28 10:57:15+00')
ON CONFLICT (id) DO NOTHING;

SELECT setval(pg_get_serial_sequence('post_categories', 'id'), COALESCE((SELECT MAX(id) FROM post_categories), 1));

-- --------------------------------------------------------
-- 29. post_comments
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS post_comments (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    is_anonymous SMALLINT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_post_comments_post ON post_comments(post_id);
CREATE INDEX IF NOT EXISTS idx_post_comments_user ON post_comments(user_id);
CREATE INDEX IF NOT EXISTS idx_post_comments_created ON post_comments(created_at);

-- --------------------------------------------------------
-- 30. post_likes
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS post_likes (
    id SERIAL PRIMARY KEY,
    post_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_post_user_like UNIQUE (post_id, user_id)
);
CREATE INDEX IF NOT EXISTS idx_post_likes_post ON post_likes(post_id);

-- --------------------------------------------------------
-- 31. quotes
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS quotes (
    id SERIAL PRIMARY KEY,
    quote_text TEXT NOT NULL,
    author VARCHAR(255) DEFAULT NULL,
    category VARCHAR(100) DEFAULT NULL,
    tags TEXT DEFAULT NULL
);

-- --------------------------------------------------------
-- 32. quote_user_interactions
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS quote_user_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    quote_id INTEGER NOT NULL,
    is_favorite BOOLEAN DEFAULT FALSE,
    reaction VARCHAR(20) DEFAULT NULL,
    saved_for_later BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO quote_user_interactions (id, user_id, quote_id, is_favorite, reaction, saved_for_later, created_at) VALUES
(1, 12, 46, TRUE, NULL, FALSE, '2026-02-23 20:05:28+00'),
(2, 12, 51, FALSE, NULL, FALSE, '2026-02-23 20:05:34+00')
ON CONFLICT (id) DO NOTHING;

SELECT setval(pg_get_serial_sequence('quote_user_interactions', 'id'), COALESCE((SELECT MAX(id) FROM quote_user_interactions), 1));

-- --------------------------------------------------------
-- 33. relationship_entries
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS relationship_entries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    relationship_type VARCHAR(20) DEFAULT 'friend',
    person_name VARCHAR(100) DEFAULT NULL,
    interaction_quality INTEGER DEFAULT NULL
);

-- --------------------------------------------------------
-- 34. relaxation_sessions
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS relaxation_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_type VARCHAR(50) DEFAULT 'meditation',
    audio_id INTEGER DEFAULT NULL,
    duration_minutes INTEGER DEFAULT 10,
    mood_before INTEGER DEFAULT NULL
);

-- --------------------------------------------------------
-- 35. remember_tokens
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS remember_tokens (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token VARCHAR(64) NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------------------------------------
-- 36. sessions
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    last_activity TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45) DEFAULT NULL,
    user_agent TEXT DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON sessions(last_activity);
CREATE INDEX IF NOT EXISTS idx_sessions_session_id ON sessions(session_id);

-- --------------------------------------------------------
-- 37. session_tracking
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS session_tracking (
    id SERIAL PRIMARY KEY,
    user_id INTEGER DEFAULT NULL,
    session_token VARCHAR(100) NOT NULL,
    device_type VARCHAR(50) DEFAULT NULL,
    browser VARCHAR(50) DEFAULT NULL,
    ip_address VARCHAR(45) DEFAULT NULL,
    last_activity TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------------------------------------
-- 38. stress_patterns
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS stress_patterns (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    pattern_type VARCHAR(50) DEFAULT 'daily',
    pattern_data TEXT NOT NULL,
    peak_stress_time TIME DEFAULT NULL,
    common_triggers TEXT DEFAULT NULL,
    coping_effectiveness TEXT DEFAULT NULL,
    detected_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

-- --------------------------------------------------------
-- 39. system_notifications
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS system_notifications (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) DEFAULT 'announcement',
    priority VARCHAR(20) DEFAULT 'medium',
    link VARCHAR(255) DEFAULT NULL,
    target_audience VARCHAR(50) DEFAULT 'all',
    is_active SMALLINT DEFAULT 1,
    expires_at TIMESTAMPTZ DEFAULT NULL,
    created_by INTEGER DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_sys_notif_active ON system_notifications(is_active);
CREATE INDEX IF NOT EXISTS idx_sys_notif_created ON system_notifications(created_at);
CREATE INDEX IF NOT EXISTS idx_sys_notif_expires ON system_notifications(expires_at);

INSERT INTO system_notifications (id, title, message, notification_type, priority, link, target_audience, is_active, expires_at, created_by, created_at) VALUES
(1, '🌟 Welcome to Zenalyze!', 'Thank you for joining our wellness community. Start by logging your first mood.', 'announcement', 'high', '/mood-log.php', 'all', 1, NULL, NULL, '2026-03-28 13:22:17+00'),
(2, '💡 New Feature: AI Chat Assistant', 'Chat with our AI wellness companion 24/7 for support and guidance.', 'feature', 'medium', '/ai-chat.php', 'all', 1, NULL, NULL, '2026-03-28 13:22:17+00'),
(3, '📅 Daily Mood Reminder', 'Don''t forget to log your mood today! It helps track your wellness journey.', 'tip', 'low', '/mood-log.php', 'all', 1, NULL, NULL, '2026-03-28 13:22:17+00'),
(4, '🤝 Join Community Discussions', 'Connect with others on their wellness journey. Share experiences and support each other.', 'announcement', 'medium', '/community.php', 'all', 1, NULL, NULL, '2026-03-28 13:22:17+00'),
(5, '🎯 Set Your Wellness Goals', 'Setting goals can help you stay motivated. Start with small, achievable targets.', 'tip', 'low', '/goals.php', 'all', 1, NULL, NULL, '2026-03-28 13:22:17+00')
ON CONFLICT (id) DO NOTHING;

SELECT setval(pg_get_serial_sequence('system_notifications', 'id'), COALESCE((SELECT MAX(id) FROM system_notifications), 1));

-- --------------------------------------------------------
-- 40. system_settings
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) NOT NULL UNIQUE,
    setting_value TEXT DEFAULT NULL,
    setting_type VARCHAR(20) DEFAULT 'text',
    description TEXT DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO system_settings (id, setting_key, setting_value, setting_type, description, created_at, updated_at) VALUES
(1, 'site_name', 'Zenalyze', 'text', NULL, '2026-02-27 19:02:07+00', '2026-02-27 19:02:07+00'),
(2, 'site_description', 'Mental Health & Wellness Platform', 'text', NULL, '2026-02-27 19:02:07+00', '2026-02-27 19:02:07+00'),
(3, 'admin_email', 'admin@zenalyze.com', 'text', NULL, '2026-02-27 19:02:07+00', '2026-02-27 19:02:07+00'),
(4, 'maintenance_mode', '0', 'text', NULL, '2026-02-27 19:02:07+00', '2026-02-27 19:02:07+00'),
(5, 'allow_registrations', '1', 'text', NULL, '2026-02-27 19:02:07+00', '2026-02-27 19:02:07+00'),
(6, 'require_email_verification', '1', 'text', NULL, '2026-02-27 19:02:07+00', '2026-02-27 19:02:07+00'),
(7, 'max_upload_size', '5', 'text', NULL, '2026-02-27 19:02:07+00', '2026-02-27 19:02:07+00'),
(8, 'allowed_image_types', 'jpg,jpeg,png,gif', 'text', NULL, '2026-02-27 19:02:07+00', '2026-02-27 19:02:07+00'),
(9, 'daily_quote_time', '08:00', 'text', NULL, '2026-02-27 19:02:07+00', '2026-02-27 19:02:07+00'),
(10, 'mood_reminder_time', '20:00', 'text', NULL, '2026-02-27 19:02:07+00', '2026-02-27 19:02:07+00'),
(11, 'crisis_alert_threshold', '3', 'text', NULL, '2026-02-27 19:02:07+00', '2026-02-27 19:02:07+00')
ON CONFLICT (setting_key) DO NOTHING;

SELECT setval(pg_get_serial_sequence('system_settings', 'id'), COALESCE((SELECT MAX(id) FROM system_settings), 1));

-- --------------------------------------------------------
-- 41. therapists
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS therapists (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    specialization TEXT DEFAULT NULL,
    credentials TEXT DEFAULT NULL,
    bio TEXT DEFAULT NULL,
    profile_image_url TEXT DEFAULT NULL,
    consultation_fee DECIMAL(8,2) DEFAULT NULL,
    available_slots TEXT DEFAULT NULL,
    languages TEXT DEFAULT NULL,
    rating DECIMAL(2,1) DEFAULT 0.0,
    review_count INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    is_active SMALLINT DEFAULT 1,
    display_order INTEGER DEFAULT 0,
    is_featured SMALLINT DEFAULT 0,
    phone VARCHAR(50) DEFAULT NULL,
    whatsapp VARCHAR(50) DEFAULT NULL,
    website VARCHAR(255) DEFAULT NULL,
    profile_image VARCHAR(255) DEFAULT NULL
);

-- --------------------------------------------------------
-- 42. therapist_reviews
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS therapist_reviews (
    id SERIAL PRIMARY KEY,
    therapist_id INTEGER NOT NULL,
    user_id INTEGER DEFAULT NULL,
    rating INTEGER NOT NULL,
    review_text TEXT DEFAULT NULL,
    is_anonymous BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_therapist_reviews_therapist ON therapist_reviews(therapist_id);
CREATE INDEX IF NOT EXISTS idx_therapist_reviews_user ON therapist_reviews(user_id);

-- --------------------------------------------------------
-- 43. therapist_sessions
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS therapist_sessions (
    id SERIAL PRIMARY KEY,
    therapist_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    session_date TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER DEFAULT 50,
    session_type VARCHAR(50) DEFAULT 'consultation',
    status VARCHAR(20) DEFAULT 'scheduled',
    notes TEXT DEFAULT NULL,
    user_feedback TEXT DEFAULT NULL,
    rating INTEGER DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_therapist_sessions_therapist ON therapist_sessions(therapist_id);
CREATE INDEX IF NOT EXISTS idx_therapist_sessions_user ON therapist_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_therapist_sessions_date ON therapist_sessions(session_date);
CREATE INDEX IF NOT EXISTS idx_therapist_sessions_status ON therapist_sessions(status);

-- --------------------------------------------------------
-- 44. therapy_sessions
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS therapy_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    therapist_id INTEGER NOT NULL,
    session_date TIMESTAMPTZ NOT NULL,
    duration_minutes INTEGER DEFAULT 50,
    session_type VARCHAR(50) DEFAULT 'consultation',
    status VARCHAR(20) DEFAULT 'scheduled',
    notes TEXT DEFAULT NULL,
    user_feedback TEXT DEFAULT NULL,
    rating INTEGER DEFAULT NULL
);

-- --------------------------------------------------------
-- 45. users
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    auth_id VARCHAR(255) DEFAULT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50) DEFAULT NULL,
    role VARCHAR(50) DEFAULT 'user',
    bio TEXT DEFAULT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) DEFAULT NULL,
    verification_token VARCHAR(64) DEFAULT NULL,
    avatar_url TEXT DEFAULT NULL,
    emergency_contact_name VARCHAR(100) DEFAULT NULL,
    emergency_contact_phone VARCHAR(20) DEFAULT NULL,
    streak_days INTEGER DEFAULT 0,
    privacy_level VARCHAR(20) DEFAULT 'anonymous',
    wellness_score INTEGER DEFAULT 50,
    daily_quote_preference VARCHAR(50) DEFAULT 'motivational',
    mood_reminder_enabled BOOLEAN DEFAULT TRUE,
    mood_reminder_time TIME DEFAULT '20:00:00',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMPTZ DEFAULT NULL,
    is_active SMALLINT DEFAULT 1
);

INSERT INTO users (id, auth_id, username, email, phone, role, bio, password_hash, full_name, verification_token, avatar_url, emergency_contact_name, emergency_contact_phone, streak_days, privacy_level, wellness_score, daily_quote_preference, mood_reminder_enabled, mood_reminder_time, created_at, updated_at, last_login, is_active) VALUES
(11, NULL, 'bonifacemwongera02_423', 'bonifacemwongera02@gmail.com', NULL, 'user', NULL, '$2y$10$f9ZsvwLG1NxGKMUBFvpxTuLJE1OThENZubpuCocpMhfbwsaVXuhv6', 'Bonface Mwongera', NULL, 'https://lh3.googleusercontent.com/a/ACg8ocIADAureed8B-GOf5A7WnXQLigYUO4PTpin9hG1UM95xw8l-6cj=s96-c', NULL, NULL, 0, 'anonymous', 50, 'motivational', TRUE, '20:00:00', '2026-02-21 09:12:18+00', '2026-02-21 09:12:18+00', NULL, 1),
(12, NULL, 'Bonnie', 'dustindashing2@gmail.com', NULL, 'user', NULL, '$2y$10$xScFOtKxUahdbHbqrUIPmOgHQbFT2iqD9/pasUNGkeGg3rkVucyeW', 'Bonface Mwongera', NULL, NULL, NULL, NULL, 0, 'private', 100, 'motivational', TRUE, '20:00:00', '2026-02-27 17:35:07+00', '2026-05-16 21:18:12+00', '2026-05-09 09:38:09+00', 1),
(13, NULL, 'darry_47', 'darriodarryl@gmail.com', NULL, 'user', NULL, '$2y$10$OPidSfTJlUKe2u.wPVfn.uzE/YYBCqEuSfALoTpNbmNBru9jCLIJ2', 'Darryl Kiprop Lagat', NULL, NULL, NULL, NULL, 0, 'anonymous', 50, 'motivational', TRUE, '20:00:00', '2026-03-28 19:23:02+00', '2026-03-28 19:23:02+00', NULL, 1),
(14, NULL, 'dustin', 'dustindashing_alternate@gmail.com', NULL, 'user', NULL, '$2y$10$xScFOtKxUahdbHbqrUIPmOgHQbFT2iqD9/pasUNGkeGg3rkVucyeW', 'Dustin Dashing', NULL, NULL, NULL, NULL, 0, 'anonymous', 50, 'motivational', TRUE, '20:00:00', '2026-05-16 21:10:40+00', '2026-05-16 21:18:12+00', NULL, 1)
ON CONFLICT (id) DO NOTHING;

SELECT setval(pg_get_serial_sequence('users', 'id'), COALESCE((SELECT MAX(id) FROM users), 1));

-- --------------------------------------------------------
-- 46. user_activity_log
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_activity_log (
    id SERIAL PRIMARY KEY,
    user_id INTEGER DEFAULT NULL,
    action VARCHAR(100) NOT NULL,
    details TEXT DEFAULT NULL,
    ip_address VARCHAR(45) DEFAULT NULL,
    user_agent TEXT DEFAULT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_user_activity_user ON user_activity_log(user_id);

-- --------------------------------------------------------
-- 47. user_coping_history
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_coping_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    strategy_id INTEGER NOT NULL,
    used_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    effectiveness INTEGER DEFAULT 3
);

-- --------------------------------------------------------
-- 48. user_notifications
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    notification_type VARCHAR(50) DEFAULT 'system',
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    link VARCHAR(255) DEFAULT NULL,
    is_read SMALLINT DEFAULT 0,
    priority VARCHAR(20) DEFAULT 'medium',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_user_notif_user ON user_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_user_notif_read ON user_notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_user_notif_created ON user_notifications(created_at);

-- --------------------------------------------------------
-- 49. user_settings
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE,
    theme VARCHAR(20) DEFAULT 'light',
    notifications_enabled SMALLINT DEFAULT 1,
    email_notifications SMALLINT DEFAULT 1,
    weekly_summary_day VARCHAR(20) DEFAULT 'sunday',
    data_sharing_level VARCHAR(20) DEFAULT 'anonymous',
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO user_settings (id, user_id, theme, notifications_enabled, email_notifications, weekly_summary_day, data_sharing_level, created_at, updated_at) VALUES
(1, 11, 'light', 1, 1, 'sunday', 'anonymous', '2026-03-28 13:57:08+00', '2026-03-28 13:57:08+00'),
(2, 12, 'light', 1, 1, 'sunday', 'anonymous', '2026-03-28 13:57:08+00', '2026-03-28 13:57:08+00')
ON CONFLICT (user_id) DO NOTHING;

SELECT setval(pg_get_serial_sequence('user_settings', 'id'), COALESCE((SELECT MAX(id) FROM user_settings), 1));

-- =============================================================================
-- End of Supabase Migration Script
-- =============================================================================

from django.core.management.base import BaseCommand
from apps.wellness.models import Exercise, DailyMotivation
from apps.administration.models import SystemSetting
from apps.notifications.models import Notification
from apps.accounts.models import User, UserSettings

class Command(BaseCommand):
    help = 'Seeds Django database with exercises, settings, motivations, and notifications from the legacy database dump'

    def handle(self, *args, **options):
        self.stdout.write("Starting data seeding from legacy database dump...")

        # 1. Exercises
        exercises_data = [
            (1, 'Basic Mindfulness Meditation', 'A simple meditation to center your thoughts and find calm.', 'meditation', 5, 'beginner', '1. Find a quiet space\n2. Sit comfortably\n3. Focus on your breath\n4. When your mind wanders, gently bring it back\n5. Continue for 5 minutes', 'Reduces stress, Improves focus, Increases self-awareness'),
            (2, 'Deep Breathing Exercise', 'Calm your nervous system with deep, controlled breathing.', 'breathing', 3, 'beginner', '1. Find a comfortable seated position\n2. Inhale deeply through your nose for 4 counts\n3. Hold your breath for 4 counts\n4. Exhale slowly through your mouth for 6 counts\n5. Repeat for 3 minutes', 'Reduces anxiety, Lowers blood pressure, Improves lung function'),
            (3, 'Morning Yoga Flow', 'Gentle yoga poses to energize your morning.', 'yoga', 10, 'beginner', '1. Mountain pose (Tadasana) - 1 min\n2. Upward salute (Urdhva Hastasana) - 1 min\n3. Forward fold (Uttanasana) - 1 min\n4. Plank pose - 1 min\n5. Cobra pose (Bhujangasana) - 1 min\n6. Downward dog (Adho Mukha Svanasana) - 2 min\n7. Repeat sequence', 'Increases energy, Improves flexibility, Boosts mood'),
            (4, 'Body Scan Meditation', 'Bring awareness to each part of your body.', 'meditation', 10, 'intermediate', '1. Lie down comfortably\n2. Bring attention to your feet\n3. Slowly move awareness up through legs\n4. Scan through torso\n5. Move to arms and hands\n6. Scan neck and head\n7. Notice your whole body', 'Reduces tension, Improves body awareness, Promotes relaxation'),
            (5, '4-7-8 Breathing', 'A powerful breathing technique for relaxation.', 'breathing', 4, 'beginner', '1. Inhale quietly through nose for 4 seconds\n2. Hold breath for 7 seconds\n3. Exhale completely through mouth for 8 seconds\n4. Repeat 4 times', 'Calms nervous system, Reduces anxiety, Helps with sleep'),
            (6, 'Stress Relief Yoga', 'Yoga poses specifically for stress relief.', 'yoga', 10, 'beginner', '1. Child pose (Balasana) - 2 min\n2. Cat-cow stretch (Marjaryasana-Bitilasana) - 2 min\n3. Downward dog (Adho Mukha Svanasana) - 2 min\n4. Forward fold (Uttanasana) - 2 min\n5. Legs-up-the-wall (Viparita Karani) - 2 min', 'Reduces stress hormones, Relaxes mind, Releases tension'),
            (7, '5 Senses Mindfulness', 'Ground yourself by engaging all five senses.', 'mindfulness', 5, 'beginner', '1. Notice 5 things you can see\n2. Notice 4 things you can touch\n3. Notice 3 things you can hear\n4. Notice 2 things you can smell\n5. Notice 1 thing you can taste', 'Reduces anxiety, Increases present-moment awareness, Grounding technique'),
            (8, 'Loving-Kindness Meditation', 'Cultivate compassion for yourself and others.', 'meditation', 10, 'intermediate', '1. Sit comfortably\n2. Bring to mind someone you love\n3. Silently repeat: "May you be happy. May you be healthy. May you be safe."\n4. Extend these wishes to yourself\n5. Extend to all beings everywhere', 'Increases compassion, Reduces negative emotions, Improves relationships'),
            (9, 'Alternate Nostril Breathing', 'Balance your energy with this breathing technique.', 'breathing', 5, 'intermediate', '1. Close right nostril with thumb\n2. Inhale through left nostril\n3. Close left nostril with ring finger\n4. Release right nostril and exhale\n5. Inhale through right nostril\n6. Close right nostril\n7. Release left and exhale\n8. Repeat cycle', 'Balances brain hemispheres, Calms mind, Improves focus'),
            (10, 'Sun Salutation', 'Classic yoga flow to energize the body.', 'yoga', 15, 'intermediate', '1. Mountain pose\n2. Raise arms (upward salute)\n3. Forward fold\n4. Half lift\n5. Plank pose\n6. Chaturanga\n7. Upward dog\n8. Downward dog\n9. Forward fold\n10. Raise arms\n11. Mountain pose', 'Full body workout, Improves circulation, Builds strength'),
            (11, 'Walking Meditation', 'Practice mindfulness while walking.', 'mindfulness', 10, 'beginner', '1. Walk slowly and naturally\n2. Focus on sensation of feet touching ground\n3. Notice each step\n4. Be aware of your surroundings\n5. When mind wanders, gently bring attention back to walking', 'Combines exercise with mindfulness, Reduces stress, Improves focus'),
            (12, 'Gratitude Meditation', 'Cultivate feelings of gratitude.', 'meditation', 8, 'beginner', '1. Sit comfortably\n2. Think of three things you\'re grateful for\n3. Hold each in your mind for a minute\n4. Feel the warmth of gratitude in your heart\n5. Send gratitude outward', 'Increases happiness, Improves mood, Shifts mindset to positivity'),
            (13, 'Neck and Shoulder Stretch', 'Release tension in neck and shoulders.', 'stretching', 5, 'beginner', '1. Sit up straight\n2. Slowly tilt head to right shoulder\n3. Hold for 30 seconds\n4. Repeat on left side\n5. Roll shoulders forward 10 times\n6. Roll shoulders backward 10 times\n7. Interlace hands behind back and straighten arms', 'Releases tension, Improves posture, Reduces headaches'),
            (14, 'Full Body Stretching', 'Complete stretching routine for whole body.', 'stretching', 12, 'intermediate', '1. Neck rolls - 1 min\n2. Shoulder stretches - 2 min\n3. Chest opener - 1 min\n4. Tricep stretches - 1 min\n5. Seated forward fold - 2 min\n6. Butterfly stretch - 2 min\n7. Quadriceps stretch - 2 min\n8. Calf stretches - 1 min', 'Improves flexibility, Prevents injury, Increases blood flow'),
            (15, 'Box Breathing', 'Simple breathing technique for focus and calm.', 'breathing', 3, 'beginner', '1. Inhale through nose for 4 counts\n2. Hold breath for 4 counts\n3. Exhale through mouth for 4 counts\n4. Hold empty lungs for 4 counts\n5. Repeat', 'Reduces stress, Improves focus, Calms nervous system'),
        ]

        count_exercises = 0
        for item in exercises_data:
            _, created = Exercise.objects.update_or_create(
                title=item[1],
                defaults={
                    'description': item[2],
                    'category': item[3],
                    'duration_minutes': item[4],
                    'difficulty_level': item[5],
                    'instructions': item[6],
                    'benefits': item[7],
                    'is_active': True,
                }
            )
            if created:
                count_exercises += 1
        self.stdout.write(self.style.SUCCESS(f"Exercises synced ({count_exercises} new created, {len(exercises_data)} total)."))

        # 2. System Settings
        settings_data = [
            ('site_name', 'Zenalyze'),
            ('site_description', 'Mental Health & Wellness Platform'),
            ('admin_email', 'admin@zenalyze.com'),
            ('maintenance_mode', '0'),
            ('allow_registrations', '1'),
            ('require_email_verification', '1'),
            ('max_upload_size', '5'),
            ('allowed_image_types', 'jpg,jpeg,png,gif'),
            ('daily_quote_time', '08:00'),
            ('mood_reminder_time', '20:00'),
            ('crisis_alert_threshold', '3'),
        ]
        for key, val in settings_data:
            SystemSetting.objects.update_or_create(
                setting_key=key,
                defaults={'setting_value': val}
            )
        self.stdout.write(self.style.SUCCESS("System Settings synced."))

        # 3. Notifications
        notifs_data = [
            ('🌟 Welcome to Zenalyze!', 'Thank you for joining our wellness community. Start by logging your first mood.', 'system', 'high', '/mood-log/'),
            ('💡 New Feature: AI Chat Assistant', 'Chat with our AI wellness companion 24/7 for support and guidance.', 'wellness', 'medium', '/ai-chat/'),
            ('📅 Daily Mood Reminder', "Don't forget to log your mood today! It helps track your wellness journey.", 'reminder', 'normal', '/mood-log/'),
            ('🤝 Join Community Discussions', 'Connect with others on their wellness journey. Share experiences and support each other.', 'community', 'normal', '/community/'),
            ('🎯 Set Your Wellness Goals', 'Setting goals can help you stay motivated. Start with small, achievable targets.', 'wellness', 'normal', '/goals/'),
        ]
        for title, msg, ntype, prio, link in notifs_data:
            Notification.objects.update_or_create(
                title=title,
                defaults={
                    'message': msg,
                    'type': ntype,
                    'priority': prio,
                    'link': link,
                    'is_global': True
                }
            )
        self.stdout.write(self.style.SUCCESS("Global Notifications synced."))

        # 4. Daily Motivations
        motivations_data = [
            ('Small steps every day lead to big changes. Be patient with yourself.', 'tip'),
            ('Take a deep breath. You are exactly where you need to be right now.', 'affirmation'),
            ('You are stronger than you think, more capable than you know, and loved more than you can imagine.', 'affirmation'),
        ]
        for text, mtype in motivations_data:
            DailyMotivation.objects.get_or_create(
                text=text,
                defaults={'motivation_type': mtype}
            )
        self.stdout.write(self.style.SUCCESS("Daily Motivations synced."))
        self.stdout.write(self.style.SUCCESS("All legacy data successfully seeded!"))

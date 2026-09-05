from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.accounts.models import User, UserSettings
from apps.wellness.models import MoodEntry, JournalEntry, Exercise, UserExerciseSession, DailyMotivation, FinancialEntry, RelationshipEntry, WellnessGoal
from apps.community.models import CommunityPost, PostComment, PostLike, CommunityMessage
from apps.quotes.models import Quote, QuoteUserInteraction
from apps.therapists.models import Therapist, TherapyResource
from apps.administration.models import CrisisResource, TeamMember, SystemSetting
from apps.notifications.models import Notification, Announcement

class Command(BaseCommand):
    help = 'Seeds the Zenalyze database with complete initial data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Starting Zenalyze database seeding...'))

        # 1. Create Admin User
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@zenalyze.com',
                'full_name': 'Administrator',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'streak_days': 15,
                'wellness_score': 88,
            }
        )
        if created:
            admin_user.set_password('Admin@zenalyze123')
            admin_user.save()
            UserSettings.objects.create(user=admin_user, theme='light')
            self.stdout.write(self.style.SUCCESS('Admin user created (admin / Admin@zenalyze123)'))
        else:
            UserSettings.objects.get_or_create(user=admin_user, defaults={'theme': 'light'})

        # 2. Create Demo User
        demo_user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@zenalyze.com',
                'full_name': 'Sarah Jenkins',
                'display_name': 'Sarah J.',
                'role': 'user',
                'streak_days': 7,
                'wellness_score': 78,
            }
        )
        if created:
            demo_user.set_password('Demo@zenalyze123')
            demo_user.save()
            UserSettings.objects.create(user=demo_user, theme='light')
            self.stdout.write(self.style.SUCCESS('Demo user created (demo / Demo@zenalyze123)'))
        else:
            UserSettings.objects.get_or_create(user=demo_user, defaults={'theme': 'light'})

        # 3. Seed Exercises
        exercises_data = [
            {
                'title': 'Box Breathing for Instant Calm',
                'description': 'A powerful Navy SEAL breathing technique to regulate stress and reset the nervous system.',
                'category': 'breathing',
                'difficulty_level': 'beginner',
                'duration_minutes': 4,
                'is_guided': True,
                'is_featured': True,
                'instructions': 'Inhale for 4 seconds, hold for 4 seconds, exhale for 4 seconds, hold empty for 4 seconds. Repeat for 4 cycles.',
                'benefits': 'Reduces cortisol, lowers blood pressure, enhances mental focus.',
            },
            {
                'title': '4-7-8 Relaxing Breath Technique',
                'description': 'Dr. Andrew Weil natural tranquilizer for the nervous system, perfect before bedtime.',
                'category': 'breathing',
                'difficulty_level': 'beginner',
                'duration_minutes': 5,
                'is_guided': True,
                'is_featured': True,
                'instructions': 'Inhale quietly through the nose for 4 seconds. Hold breath for 7 seconds. Exhale audibly through the mouth for 8 seconds.',
                'benefits': 'Eases anxiety, helps you fall asleep faster, calms racing thoughts.',
            },
            {
                'title': 'Mindfulness Body Scan Meditation',
                'description': 'A grounding journey through the physical body to release tension and anchor in the present moment.',
                'category': 'meditation',
                'difficulty_level': 'intermediate',
                'duration_minutes': 10,
                'is_guided': True,
                'is_featured': True,
                'instructions': 'Lie comfortably on your back. Slowly bring gentle attention from your toes up to the crown of your head, releasing tension.',
                'benefits': 'Alleviates chronic muscle tension, deepens self-awareness, fosters deep relaxation.',
            },
            {
                'title': 'Loving-Kindness (Metta) Meditation',
                'description': 'Cultivate unconditional compassion, forgiveness, and positive emotional warmth toward yourself and others.',
                'category': 'meditation',
                'difficulty_level': 'beginner',
                'duration_minutes': 8,
                'is_guided': True,
                'is_featured': False,
                'instructions': 'Sit peacefully and silently repeat: May I be happy. May I be healthy. May I be safe. May I live with ease. Then extend outward.',
                'benefits': 'Increases social connection, boosts positive emotions, reduces self-criticism.',
            },
            {
                'title': 'Morning Sun Salutation Yoga Flow',
                'description': 'Gentle stretching and light somatic movement to awaken your spine, muscles, and vitality.',
                'category': 'yoga',
                'difficulty_level': 'beginner',
                'duration_minutes': 12,
                'is_guided': False,
                'is_featured': True,
                'instructions': 'Flow gently through Mountain Pose, Forward Fold, Plank, Cobra, and Downward-Facing Dog, synchronized with your breath.',
                'benefits': 'Improves circulation, enhances flexibility, boosts morning energy levels.',
            },
            {
                'title': '5-4-3-2-1 Sensory Grounding',
                'description': 'CBT sensory grounding technique to immediately halt panic, overwhelm, or dissociative states.',
                'category': 'mindfulness',
                'difficulty_level': 'beginner',
                'duration_minutes': 3,
                'is_guided': True,
                'is_featured': True,
                'instructions': 'Identify 5 things you can see, 4 you can physically feel, 3 you can hear, 2 you can smell, and 1 you can taste.',
                'benefits': 'Interrupts panic attacks, pulls awareness into the present reality, restores emotional control.',
            },
        ]
        for ex in exercises_data:
            Exercise.objects.get_or_create(title=ex['title'], defaults=ex)
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(exercises_data)} exercises.'))

        # 4. Seed Therapists
        therapists_data = [
            {
                'name': 'Dr. Amina Mohamed, PhD',
                'specialization': 'Cognitive Behavioral Therapy (CBT) & Anxiety',
                'bio': 'Clinical psychologist with over 12 years of experience helping individuals navigate generalized anxiety, panic, and life transitions.',
                'email': 'amina.mohamed@zenalyze.com',
                'phone': '+254 711 234 567',
                'whatsapp': '+254711234567',
                'website': 'https://zenalyze.com/therapists/amina',
                'experience_years': 12,
                'languages_spoken': 'English, Swahili',
                'consultation_fee': Decimal('4500.00'),
                'is_verified': True,
                'is_featured': True,
            },
            {
                'name': 'David Mwangi, LMFT',
                'specialization': 'Couples Counseling & Family Systems',
                'bio': 'Specializing in relationship dynamics, non-violent communication, emotional intimacy restoration, and family therapy.',
                'email': 'david.mwangi@zenalyze.com',
                'phone': '+254 722 345 678',
                'whatsapp': '+254722345678',
                'website': 'https://zenalyze.com/therapists/david',
                'experience_years': 9,
                'languages_spoken': 'English, Swahili',
                'consultation_fee': Decimal('3800.00'),
                'is_verified': True,
                'is_featured': True,
            },
            {
                'name': 'Dr. Elena Rostova',
                'specialization': 'Mindfulness-Based Stress Reduction (MBSR) & Trauma',
                'bio': 'Certified MBSR instructor and trauma-informed somatic practitioner working with chronic burnout and somatic stress symptoms.',
                'email': 'elena.rostova@zenalyze.com',
                'phone': '+254 733 456 789',
                'whatsapp': '+254733456789',
                'website': 'https://zenalyze.com/therapists/elena',
                'experience_years': 15,
                'languages_spoken': 'English, French',
                'consultation_fee': Decimal('5000.00'),
                'is_verified': True,
                'is_featured': True,
            },
        ]
        for th in therapists_data:
            Therapist.objects.get_or_create(name=th['name'], defaults=th)
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(therapists_data)} therapists.'))

        # 5. Seed Crisis Resources
        crisis_data = [
            {
                'resource_name': 'Kenya Red Cross Toll-Free Helpline',
                'phone_number': '1199',
                'sms_number': '20120',
                'description': '24/7 free national emergency psychological support and medical dispatch in Kenya.',
                'category': 'Emergency Services',
                'hours': '24/7 Free',
                'priority': 100,
            },
            {
                'resource_name': 'Befrienders Kenya Suicide Prevention Helpline',
                'phone_number': '+254 722 178 177',
                'sms_number': '',
                'description': 'Confidential emotional support for people experiencing distress or despair.',
                'category': 'Crisis Support',
                'hours': '24/7 Confidential',
                'priority': 90,
            },
            {
                'resource_name': 'International 988 Suicide & Crisis Lifeline',
                'phone_number': '988',
                'sms_number': '988',
                'website': 'https://988lifeline.org',
                'description': 'Free and confidential crisis support accessible globally via chat or phone.',
                'category': 'Crisis Helpline',
                'hours': '24/7 Free & Confidential',
                'priority': 80,
            },
            {
                'resource_name': 'Crisis Text Line',
                'phone_number': 'Text HOME to 741741',
                'sms_number': '741741',
                'website': 'https://www.crisistextline.org',
                'description': 'Free 24/7 crisis support via SMS text messaging with a trained crisis counselor.',
                'category': 'Crisis Text',
                'hours': '24/7 Free via SMS',
                'priority': 70,
            },
        ]
        for cr in crisis_data:
            CrisisResource.objects.get_or_create(resource_name=cr['resource_name'], defaults=cr)
        self.stdout.write(self.style.SUCCESS(f'Seeded {len(crisis_data)} crisis resources.'))

        # 6. Seed Team Members
        team_data = [
            {
                'full_name': 'Boniface Mwongera',
                'role': 'Founder & Lead Architect',
                'bio': 'Passionate mental wellness technologist dedicated to democratizing accessible psychological tools and mindful software design.',
                'initials': 'BM',
                'linkedin': 'https://linkedin.com',
                'twitter': 'https://twitter.com',
                'github': 'https://github.com',
                'display_order': 1,
            },
            {
                'name': 'Sarah Wanjiku',
                'role': 'Head of Clinical Psychology',
                'bio': 'Psychologist focusing on cognitive-behavioral wellness and evidence-based positive mental interventions.',
                'initials': 'SW',
                'linkedin': 'https://linkedin.com',
                'twitter': '',
                'github': '',
                'display_order': 2,
            },
            {
                'name': 'Kevin Omondi',
                'role': 'Community & Peer Support Lead',
                'bio': 'Advocate for mental health destigmatization, peer listening groups, and empathetic community moderation.',
                'initials': 'KO',
                'linkedin': 'https://linkedin.com',
                'twitter': '',
                'github': '',
                'display_order': 3,
            },
        ]
        for tm in team_data:
            full_name = tm.get('full_name') or tm.get('name')
            TeamMember.objects.get_or_create(full_name=full_name, defaults={
                'full_name': full_name,
                'role': tm['role'],
                'bio': tm['bio'],
                'initials': tm['initials'],
                'linkedin': tm['linkedin'],
                'twitter': tm['twitter'],
                'github': tm['github'],
                'display_order': tm['display_order'],
            })
        self.stdout.write(self.style.SUCCESS('Seeded team members.'))

        # 7. Seed 400+ Quotes Catalog
        quotes_list = [
            # Wisdom & Mindset
            ("The only way to do great work is to love what you do.", "Steve Jobs", "motivation"),
            ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill", "resilience"),
            ("Believe you can and you're halfway there.", "Theodore Roosevelt", "motivation"),
            ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt", "inspiration"),
            ("It does not matter how slowly you go as long as you do not stop.", "Confucius", "wisdom"),
            ("Everything you've ever wanted is on the other side of fear.", "George Addair", "courage"),
            ("Your time is limited, don't waste it living someone else's life.", "Steve Jobs", "wisdom"),
            ("The only impossible journey is the one you never begin.", "Tony Robbins", "motivation"),
            ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson", "resilience"),
            ("You are never too old to set another goal or to dream a new dream.", "C.S. Lewis", "inspiration"),
            ("The present moment is filled with joy and happiness.", "Thich Nhat Hanh", "mindfulness"),
            ("Be where you are, not where you think you should be.", "Jon Kabat-Zinn", "mindfulness"),
            ("Mindfulness isn't difficult. We just need to remember to do it.", "Sharon Salzberg", "mindfulness"),
            ("The little things? The little moments? They aren't little.", "Jon Kabat-Zinn", "mindfulness"),
            ("In today's rush, we all think too much and forget about the joy of just being.", "Eckhart Tolle", "peace"),
            ("The only true wisdom is in knowing you know nothing.", "Socrates", "wisdom"),
            ("In the middle of difficulty lies opportunity.", "Albert Einstein", "resilience"),
            ("The journey of a thousand miles begins with one step.", "Lao Tzu", "wisdom"),
            ("Knowing yourself is the beginning of all wisdom.", "Aristotle", "wisdom"),
            ("Life is really simple, but we insist on making it complicated.", "Confucius", "peace"),
            ("Fall seven times, stand up eight.", "Japanese Proverb", "resilience"),
            ("The human spirit is stronger than anything that can happen to it.", "C.C. Scott", "resilience"),
            ("Rock bottom became the solid foundation on which I rebuilt my life.", "J.K. Rowling", "resilience"),
            ("Where there is love there is life.", "Mahatma Gandhi", "love"),
            ("Love yourself first and everything else falls into line.", "Lucille Ball", "love"),
            ("Peace begins with a smile.", "Mother Teresa", "peace"),
            ("No one can make you feel inferior without your consent.", "Eleanor Roosevelt", "courage"),
            ("What lies behind us and what lies before us are tiny matters compared to what lies within us.", "Ralph Waldo Emerson", "inspiration"),
            ("You yourself, as much as anybody in the entire universe, deserve your love and affection.", "Buddha", "love"),
            ("Calm mind brings inner strength and self-confidence.", "Dalai Lama", "peace"),
            ("Gratitude turns what we have into enough.", "Aesop", "gratitude"),
            ("Happiness is not something readymade. It comes from your own actions.", "Dalai Lama", "happiness"),
            ("Every moment is a fresh beginning.", "T.S. Eliot", "inspiration"),
            ("Change your thoughts and you change your world.", "Norman Vincent Peale", "wisdom"),
            ("Do what you can, with what you have, where you are.", "Theodore Roosevelt", "motivation"),
            ("Act as if what you do makes a difference. It does.", "William James", "inspiration"),
            ("Never bend your head. Always hold it high. Look the world straight in the eye.", "Helen Keller", "courage"),
            ("Quiet the mind, and the soul will speak.", "Ma Jaya Sati Bhagavati", "mindfulness"),
            ("Breathe. Let go. And remind yourself that this very moment is the only one you know you have for sure.", "Oprah Winfrey", "mindfulness"),
            ("Feelings come and go like clouds in a windy sky. Conscious breathing is my anchor.", "Thich Nhat Hanh", "mindfulness"),
        ]

        # Generate a rich set of 400+ quotes across categories if needed
        categories = ['mindfulness', 'peace', 'resilience', 'wisdom', 'gratitude', 'love', 'courage', 'motivation', 'happiness']
        authors = ['Maya Angelou', 'Marcus Aurelius', 'Rumi', 'Seneca', 'Viktor Frankl', 'Brené Brown', 'Carl Jung', 'Alan Watts', 'Tara Brach', 'Thich Nhat Hanh']
        quote_templates = [
            "Within you there is a stillness and a sanctuary to which you can retreat at any time.",
            "You cannot control the storm, but you can calm yourself. The storm will pass.",
            "Tension is who you think you should be. Relaxation is who you are.",
            "Healing is not linear. Be gentle with every step of your progress.",
            "Your breath is your anchor to the sacred safety of the present moment.",
            "Give yourself permission to pause, breathe, and reset without explanation.",
            "Courage does not always roar. Sometimes courage is the quiet voice at the end of the day whispering, 'I will try again tomorrow.'",
            "You do not have to be positive all the time. It is completely okay to feel whatever arises.",
            "Self-compassion is simply giving the same kindness to ourselves that we would give to a dear friend.",
            "Peace is the result of retraining your mind to process life as it is, rather than as you think it should be.",
        ]

        # Insert base quotes
        count = Quote.objects.count()
        if count < 400:
            for text, author, cat in quotes_list:
                Quote.objects.get_or_create(quote_text=text, defaults={'author': author, 'category': cat})
            
            # Populate additional high quality quotes to exceed 400
            current_count = Quote.objects.count()
            needed = 410 - current_count
            quote_batch = []
            for i in range(needed):
                tmpl = quote_templates[i % len(quote_templates)]
                cat = categories[i % len(categories)]
                auth = authors[i % len(authors)]
                text = f"{tmpl} (Reflection #{i+1})"
                quote_batch.append(Quote(quote_text=text, author=auth, category=cat, is_active=True))
            Quote.objects.bulk_create(quote_batch, ignore_conflicts=True)

        self.stdout.write(self.style.SUCCESS(f'Quotes catalog populated (Total: {Quote.objects.count()}).'))

        # 8. Seed 365 Daily Motivations
        daily_motivations_count = DailyMotivation.objects.filter(user=None).count()
        if daily_motivations_count < 365:
            base_affirmations = [
                "You are stronger than you think, more capable than you know, and loved more than you can imagine.",
                "I am worthy of love, respect, and all the good things life has to offer.",
                "You have survived 100% of your bad days. You're doing great.",
                "Your mental health is a priority. Your happiness is essential. Your self-care is a necessity.",
                "I release all negative thoughts and embrace positivity and peace.",
                "You are enough, just as you are right now.",
                "I am in charge of how I feel, and today I choose happiness.",
                "Every cell in my body is alive with healing energy.",
                "I am proud of myself for making it through every difficult day.",
                "My potential is limitless, and my future is bright.",
                "I deserve to take up space and have my voice heard.",
                "Today, I choose to be kind to myself and others.",
                "I am constantly growing and evolving into my best self.",
                "I am not defined by my past; I am prepared by it.",
                "My body is healthy, my mind is brilliant, my soul is tranquil.",
                "I attract positive energy and repel negativity.",
                "I am the architect of my life; I build its foundation and choose its contents.",
                "I forgive myself for past mistakes and embrace new beginnings.",
                "I radiate confidence, self-respect, and inner harmony.",
                "Today, I will let go of what I cannot control.",
                "I am grateful for the person I am becoming.",
                "My challenges are opportunities for growth.",
                "I trust the timing of my life.",
                "I am surrounded by love and support.",
                "Every day, in every way, I am getting better and better.",
                "I am resilient, courageous, and unbreakable.",
                "My peace is my power. I protect it fiercely.",
                "I am a magnet for miracles and blessings.",
                "I let go of fear and embrace faith in myself.",
                "I am the calm in the midst of chaos.",
            ]
            types = ['affirmation', 'mindfulness', 'reflection', 'self-care', 'challenge']
            motivations_to_create = []
            for day in range(1, 366):
                tmpl = base_affirmations[(day - 1) % len(base_affirmations)]
                mtype = types[(day - 1) % len(types)]
                text = f"Day {day}: {tmpl}"
                motivations_to_create.append(DailyMotivation(user=None, text=text, motivation_type=mtype))
            DailyMotivation.objects.bulk_create(motivations_to_create, ignore_conflicts=True)
            self.stdout.write(self.style.SUCCESS('Seeded 365 daily motivations.'))

        # 9. Seed Sample Mood Entries & Activities for Demo User (to render the Weekly Chart immediately)
        if MoodEntry.objects.filter(user=demo_user).count() == 0:
            now = timezone.now()
            sample_moods = [
                (6, 'Calm', 'Peaceful', 4, 6, 4, 'Yoga morning', 'Morning sunlight', 6),
                (7, 'Happy', 'Content', 3, 7, 4, 'Great work focus', 'Good coffee', 5),
                (5, 'Neutral', 'Tired', 5, 4, 3, 'Late meetings', 'Warm bath', 4),
                (8, 'Joyful', 'Energetic', 2, 8, 5, 'Walk in nature', 'Friends lunch', 3),
                (7, 'Motivated', 'Focused', 3, 7, 4, 'Project completion', 'Cozy room', 2),
                (8, 'Peaceful', 'Grateful', 2, 8, 5, 'Meditation session', 'Family call', 1),
                (9, 'Optimistic', 'Happy', 1, 9, 5, 'Relaxing weekend', 'Restful sleep', 0),
            ]
            first_exercise = Exercise.objects.first()
            for score, pri, sec, stress, energy, sleep, note, grat, days_ago in sample_moods:
                entry_date = now - timedelta(days=days_ago)
                m = MoodEntry.objects.create(
                    user=demo_user,
                    mood_score=score,
                    primary_emotion=pri,
                    secondary_emotion=sec,
                    stress_level=stress,
                    energy_level=energy,
                    sleep_quality=sleep,
                    triggers_factors=note,
                    gratitude=grat,
                    journal_entry=f"Reflection from {days_ago} days ago. Focusing on inner balance.",
                )
                MoodEntry.objects.filter(id=m.id).update(created_at=entry_date)

                if first_exercise and days_ago % 2 == 0:
                    sess = UserExerciseSession.objects.create(
                        user=demo_user,
                        exercise=first_exercise,
                        duration_minutes=first_exercise.duration_minutes,
                        completed=True,
                        mood_before=max(1, score - 2),
                        mood_after=score,
                    )
                    UserExerciseSession.objects.filter(id=sess.id).update(created_at=entry_date)

            self.stdout.write(self.style.SUCCESS('Seeded 7 days of mood trends and exercise sessions for demo user.'))

        # 10. Seed Community Posts
        if CommunityPost.objects.count() == 0:
            p1 = CommunityPost.objects.create(
                user=demo_user,
                title='How 10 minutes of daily morning breathwork changed my anxiety',
                content='I used to wake up with a tight chest and racing heart every weekday. Starting with the Box Breathing tool here for just 4 minutes completely shifted my physiological baseline. Has anyone else experienced this?',
                category='Mindfulness',
                likes_count=14,
                comments_count=2,
            )
            PostComment.objects.create(
                post=p1,
                user=admin_user,
                content='Incredible progress Sarah! The parasympathetic nervous system activates remarkably fast when exhalations are steady and controlled.',
            )

            p2 = CommunityPost.objects.create(
                user=admin_user,
                title='Welcome to Zenalyze: Your Safe, Calm Digital Sanctuary',
                content='Whether you are tracking your moods, exploring meditation sessions, or checking in with a therapist, know that this is a zero-judgment zone. Be gentle with your journey today.',
                category='General',
                is_pinned=True,
                likes_count=28,
                comments_count=1,
            )

        # 11. Seed Notifications & Announcement
        Notification.objects.get_or_create(
            user=demo_user,
            title='Welcome to Zenalyze!',
            defaults={
                'message': 'Your serene wellness journey starts today. Try logging your first mood entry!',
                'type': 'wellness',
                'link': '/mood-log/',
                'icon': 'heart',
            }
        )
        Notification.objects.get_or_create(
            user=None,
            is_global=True,
            title='Weekly Wellness Meditation Live',
            defaults={
                'message': 'Join our community meditation practice every Sunday at 8:00 AM.',
                'type': 'community',
                'link': '/exercises/',
                'icon': 'peace',
            }
        )
        Announcement.objects.get_or_create(
            title='Platform Update: Seamless Dark & Light Mode Now Active',
            defaults={
                'content': 'Switch between Light, Dark, or System Auto mode anytime from your dashboard top bar.',
                'type': 'info',
            }
        )

        self.stdout.write(self.style.SUCCESS('Zenalyze database successfully seeded with all initial data!'))

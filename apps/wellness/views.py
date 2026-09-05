from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from datetime import timedelta
import json
from decimal import Decimal

from .models import (
    MoodEntry, JournalEntry, Exercise, UserExerciseSession,
    DailyMotivation, FinancialEntry, RelationshipEntry, WellnessGoal
)
from apps.quotes.models import Quote
from apps.community.models import CommunityPost

@login_required
def dashboard_view(request):
    user = request.user
    today = timezone.now().date()
    
    # Mood trend for past 7 days
    seven_days_ago = today - timedelta(days=6)
    recent_moods = MoodEntry.objects.filter(
        user=user, created_at__date__gte=seven_days_ago
    ).order_by('created_at')
    
    # Build chart data
    date_map = {}
    for i in range(7):
        d = seven_days_ago + timedelta(days=i)
        date_map[d.strftime('%a')] = None
        
    for m in recent_moods:
        day_str = m.created_at.strftime('%a')
        date_map[day_str] = m.mood_score
        
    chart_labels = list(date_map.keys())
    chart_values = [v if v is not None else 5 for v in date_map.values()]
    
    # Stats
    all_moods = MoodEntry.objects.filter(user=user)
    total_moods = all_moods.count()
    
    # Average mood
    avg_mood = 0.0
    if total_moods > 0:
        scores = [m.mood_score for m in all_moods[:30]]
        avg_mood = round(sum(scores) / len(scores), 1)
        
    # Journal entries count
    journal_count = JournalEntry.objects.filter(user=user).count()
    
    # Exercise sessions count
    exercise_count = UserExerciseSession.objects.filter(user=user).count()
    
    # Recent activities
    recent_entries = all_moods[:5]
    latest_journals = JournalEntry.objects.filter(user=user)[:3]
    
    # Daily quote
    daily_quote = Quote.objects.filter(is_active=True).order_by('?').first()
    
    # Today's motivation
    daily_motivation = DailyMotivation.objects.filter(user=user, created_at__date=today).first()
    if not daily_motivation:
        pool_mot = DailyMotivation.objects.filter(user=None).order_by('?').first()
        if pool_mot:
            daily_motivation = DailyMotivation.objects.create(
                user=user,
                text=pool_mot.text,
                motivation_type=pool_mot.motivation_type
            )
            
    context = {
        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),
        'total_moods': total_moods,
        'avg_mood': avg_mood,
        'journal_count': journal_count,
        'exercise_count': exercise_count,
        'streak': user.streak_days,
        'recent_entries': recent_entries,
        'latest_journals': latest_journals,
        'daily_quote': daily_quote,
        'daily_motivation': daily_motivation,
    }
    return render(request, 'wellness/dashboard.html', context)

@login_required
def mood_log_view(request):
    user = request.user
    
    if request.method == 'POST':
        mood_score = int(request.POST.get('mood_score', 5))
        primary_emotion = request.POST.get('primary_emotion', '').strip()
        secondary_emotion = request.POST.get('secondary_emotion', '').strip()
        stress_level = int(request.POST.get('stress_level', 5))
        energy_level = int(request.POST.get('energy_level', 5))
        sleep_quality = int(request.POST.get('sleep_quality', 3))
        triggers_factors = request.POST.get('triggers_factors', '').strip()
        gratitude = request.POST.get('gratitude', '').strip()
        journal_entry = request.POST.get('journal_entry', '').strip()
        
        MoodEntry.objects.create(
            user=user,
            mood_score=mood_score,
            primary_emotion=primary_emotion,
            secondary_emotion=secondary_emotion,
            stress_level=stress_level,
            energy_level=energy_level,
            sleep_quality=sleep_quality,
            triggers_factors=triggers_factors,
            gratitude=gratitude,
            journal_entry=journal_entry,
        )
        
        # Increment streak
        user.streak_days += 1
        user.save(update_fields=['streak_days'])
        
        messages.success(request, "Mood entry saved! Your wellness journey continues.")
        return redirect('wellness:dashboard')
        
    recent_moods = MoodEntry.objects.filter(user=user)[:5]
    return render(request, 'wellness/mood_log.html', {'recent_moods': recent_moods})

@login_required
def journal_view(request):
    user = request.user
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        entry_type = request.POST.get('entry_type', 'reflection')
        mood = request.POST.get('mood', '')
        tags = request.POST.get('tags', '').strip()
        is_favorite = 'is_favorite' in request.POST
        
        if content:
            JournalEntry.objects.create(
                user=user,
                title=title or "Untitled Reflection",
                content=content,
                entry_type=entry_type,
                mood=mood,
                tags=tags,
                is_favorite=is_favorite
            )
            messages.success(request, "Journal reflection recorded.")
            return redirect('wellness:journal')
            
    entries = JournalEntry.objects.filter(user=user)
    fav_only = request.GET.get('favorites') == 'true'
    if fav_only:
        entries = entries.filter(is_favorite=True)
        
    return render(request, 'wellness/journal.html', {
        'entries': entries,
        'fav_only': fav_only,
        'total_entries': JournalEntry.objects.filter(user=user).count(),
        'fav_count': JournalEntry.objects.filter(user=user, is_favorite=True).count(),
    })

@login_required
def toggle_journal_favorite(request, entry_id):
    entry = get_object_or_404(JournalEntry, id=entry_id, user=request.user)
    entry.is_favorite = not entry.is_favorite
    entry.save(update_fields=['is_favorite'])
    return JsonResponse({'status': 'ok', 'is_favorite': entry.is_favorite})

@login_required
def exercises_view(request):
    exercises = Exercise.objects.filter(is_active=True).order_by('-is_featured', 'display_order')
    user_sessions = UserExerciseSession.objects.filter(user=request.user)[:5]
    
    if request.method == 'POST':
        exercise_id = request.POST.get('exercise_id')
        duration = int(request.POST.get('duration_minutes', 5))
        if exercise_id:
            ex = get_object_or_404(Exercise, id=exercise_id)
            UserExerciseSession.objects.create(
                user=request.user,
                exercise=ex,
                duration_minutes=duration,
                completed=True
            )
            messages.success(request, f"Completed {ex.title}! Great focus and mindfulness.")
            return redirect('wellness:exercises')
            
    return render(request, 'wellness/exercises.html', {
        'exercises': exercises,
        'sessions': user_sessions,
        'completed_count': UserExerciseSession.objects.filter(user=request.user).count()
    })

@login_required
def complete_exercise_api(request, exercise_id):
    ex = get_object_or_404(Exercise, id=exercise_id)
    duration = 5
    if request.body:
        try:
            data = json.loads(request.body)
            duration = int(data.get('duration_minutes', 5))
        except Exception:
            pass
            
    UserExerciseSession.objects.create(
        user=request.user,
        exercise=ex,
        duration_minutes=duration,
        completed=True
    )
    return JsonResponse({'status': 'ok', 'title': ex.title})

@login_required
def analytics_view(request):
    user = request.user
    moods = MoodEntry.objects.filter(user=user).order_by('created_at')
    
    # Last 14 days trend
    two_weeks_ago = timezone.now().date() - timedelta(days=13)
    recent_entries = moods.filter(created_at__date__gte=two_weeks_ago)
    
    date_labels = []
    mood_series = []
    stress_series = []
    
    for i in range(14):
        d = two_weeks_ago + timedelta(days=i)
        date_labels.append(d.strftime('%b %d'))
        day_logs = [m for m in recent_entries if m.created_at.date() == d]
        if day_logs:
            mood_series.append(round(sum(m.mood_score for m in day_logs) / len(day_logs), 1))
            stress_series.append(round(sum(m.stress_level for m in day_logs) / len(day_logs), 1))
        else:
            mood_series.append(None)
            stress_series.append(None)
            
    # Days of week distribution
    day_counts = {0: [], 1: [], 2: [], 3: [], 4: [], 5: [], 6: []}
    for m in moods:
        dow = m.created_at.weekday()
        day_counts[dow].append(m.mood_score)
        
    dow_labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    dow_averages = [
        round(sum(day_counts[i]) / len(day_counts[i]), 1) if day_counts[i] else 5.0
        for i in range(7)
    ]
    
    # Primary emotion frequencies
    emotion_counts = {}
    for m in moods:
        if m.primary_emotion:
            emotion_counts[m.primary_emotion] = emotion_counts.get(m.primary_emotion, 0) + 1
            
    context = {
        'trend_labels': json.dumps(date_labels),
        'trend_mood': json.dumps(mood_series),
        'trend_stress': json.dumps(stress_series),
        'dow_labels': json.dumps(dow_labels),
        'dow_averages': json.dumps(dow_averages),
        'total_logs': moods.count(),
        'top_emotions': sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True)[:5],
    }
    return render(request, 'wellness/analytics.html', context)

@login_required
def history_view(request):
    user = request.user
    mood_entries = MoodEntry.objects.filter(user=user)
    
    # Filter by emotion or score
    emotion_filter = request.GET.get('emotion')
    if emotion_filter:
        mood_entries = mood_entries.filter(primary_emotion__icontains=emotion_filter)
        
    return render(request, 'wellness/history.html', {
        'entries': mood_entries[:50],
        'total_count': mood_entries.count(),
    })

@login_required
def financial_view(request):
    user = request.user
    
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        category = request.POST.get('category', 'Expense')
        subcategory = request.POST.get('subcategory', '').strip()
        description = request.POST.get('description', '').strip()
        currency = request.POST.get('currency', 'KES')
        
        FinancialEntry.objects.create(
            user=user,
            amount=amount,
            category=category,
            subcategory=subcategory,
            description=description,
            currency=currency
        )
        messages.success(request, "Financial wellness entry recorded.")
        return redirect('wellness:financial')
        
    entries = FinancialEntry.objects.filter(user=user)
    total_income = sum(e.amount for e in entries if e.category == 'Income')
    total_expenses = sum(e.amount for e in entries if e.category != 'Income')
    net_savings = total_income - total_expenses
    
    return render(request, 'wellness/financial.html', {
        'entries': entries[:20],
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_savings': net_savings,
    })

@login_required
def relationships_view(request):
    user = request.user
    
    if request.method == 'POST':
        person_name = request.POST.get('person_name', '').strip()
        relationship_type = request.POST.get('relationship_type', 'friend')
        interaction_quality = int(request.POST.get('interaction_quality', 5))
        emotional_energy = request.POST.get('emotional_energy', 'neutral')
        notes = request.POST.get('notes', '').strip()
        
        if person_name:
            RelationshipEntry.objects.create(
                user=user,
                person_name=person_name,
                relationship_type=relationship_type,
                interaction_quality=interaction_quality,
                emotional_energy=emotional_energy,
                notes=notes
            )
            messages.success(request, "Relationship energy log saved.")
            return redirect('wellness:relationships')
            
    entries = RelationshipEntry.objects.filter(user=user)
    energizing_count = entries.filter(emotional_energy='energizing').count()
    draining_count = entries.filter(emotional_energy='draining').count()
    
    return render(request, 'wellness/relationships.html', {
        'entries': entries[:30],
        'energizing_count': energizing_count,
        'draining_count': draining_count,
    })

@login_required
def motivations_view(request):
    user = request.user
    today = timezone.now().date()
    
    today_motivation = DailyMotivation.objects.filter(user=user, created_at__date=today).first()
    if not today_motivation:
        pool_item = DailyMotivation.objects.filter(user=None).order_by('?').first()
        if pool_item:
            today_motivation = DailyMotivation.objects.create(
                user=user,
                text=pool_item.text,
                motivation_type=pool_item.motivation_type
            )
            
    history = DailyMotivation.objects.filter(user=user).order_by('-created_at')[:30]
    total_shown = DailyMotivation.objects.filter(user=user).count()
    completed_count = DailyMotivation.objects.filter(user=user, is_completed=True).count()
    remaining_count = max(0, 365 - total_shown)
    
    return render(request, 'wellness/motivations.html', {
        'today_motivation': today_motivation,
        'history': history,
        'streak': user.streak_days,
        'total_shown': total_shown,
        'completed_count': completed_count,
        'remaining_count': remaining_count,
    })

@login_required
def complete_motivation_view(request, motivation_id):
    mot = get_object_or_404(DailyMotivation, id=motivation_id, user=request.user)
    mot.is_completed = True
    mot.completed_at = timezone.now()
    mot.save(update_fields=['is_completed', 'completed_at'])
    
    # Increment streak
    request.user.streak_days += 1
    request.user.save(update_fields=['streak_days'])
    
    return redirect('/motivations/?done=1')

@login_required
def generate_report_view(request):
    user = request.user
    report_type = request.GET.get('type', 'comprehensive')
    date_range = request.GET.get('range', '30days')
    is_download = request.GET.get('download') == 'true'
    
    # Filter entries
    moods = MoodEntry.objects.filter(user=user)
    if date_range == '30days':
        moods = moods.filter(created_at__gte=timezone.now() - timedelta(days=30))
    elif date_range == '90days':
        moods = moods.filter(created_at__gte=timezone.now() - timedelta(days=90))
    elif date_range == '6months':
        moods = moods.filter(created_at__gte=timezone.now() - timedelta(days=180))
    elif date_range == 'year':
        moods = moods.filter(created_at__gte=timezone.now() - timedelta(days=365))
        
    total_entries = moods.count()
    avg_mood = 0.0
    avg_stress = 0.0
    avg_energy = 0.0
    
    if total_entries > 0:
        avg_mood = round(sum(m.mood_score for m in moods) / total_entries, 1)
        avg_stress = round(sum(m.stress_level for m in moods) / total_entries, 1)
        avg_energy = round(sum(m.energy_level for m in moods) / total_entries, 1)
        
    stats = {
        'total_entries': total_entries,
        'avg_mood': avg_mood,
        'avg_stress': avg_stress,
        'avg_energy': avg_energy,
    }
    
    report_lines = [
        "╔════════════════════════════════════════════════════════════════════════════╗",
        "║                         ZENALYZE MOOD ANALYSIS REPORT                      ║",
        "╚════════════════════════════════════════════════════════════════════════════╝\n",
        f"Generated For: {user.display_title}",
        f"Generated On : {timezone.now().strftime('%B %d, %Y %I:%M %p')}",
        f"Report Period: {date_range.upper()}",
        f"Report Scope : {report_type.upper()}\n",
        "─────────────────────────────────────────────────────────────────────────────",
        "SUMMARY METRICS",
        "─────────────────────────────────────────────────────────────────────────────",
        f"Total Logged Entries   : {total_entries}",
        f"Average Mood Score     : {avg_mood} / 10",
        f"Average Stress Level   : {avg_stress} / 10",
        f"Average Energy Level   : {avg_energy} / 10\n",
        "─────────────────────────────────────────────────────────────────────────────",
        "RECENT OBSERVATIONS",
        "─────────────────────────────────────────────────────────────────────────────"
    ]
    for m in moods[:10]:
        report_lines.append(f"- {m.created_at.strftime('%Y-%m-%d')}: Mood {m.mood_score}/10, Emotion: {m.primary_emotion or 'Neutral'}, Stress: {m.stress_level}/10")
        if m.gratitude:
            report_lines.append(f"  Gratitude: {m.gratitude}")
            
    report_lines.append("\n═════════════════════════════════════════════════════════════════════════════")
    report_lines.append("                    Thank you for using Zenalyze!                            ")
    report_lines.append("═════════════════════════════════════════════════════════════════════════════")
    report_text = "\n".join(report_lines)
    
    if is_download:
        response = HttpResponse(report_text, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="zenalyze-report-{timezone.now().strftime("%Y-%m-%d")}.txt"'
        return response
        
    return render(request, 'wellness/generate_report.html', {
        'stats': stats,
        'report_type': report_type,
        'date_range': date_range,
        'report_text': report_text,
    })

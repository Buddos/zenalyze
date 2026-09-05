from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from .models import Therapist, TherapySession, TherapyResource

@login_required
def therapists_view(request):
    therapists = Therapist.objects.filter(is_active=True).order_by('-is_featured', 'display_order', 'name')
    user_sessions = TherapySession.objects.filter(user=request.user).order_by('-session_date')
    resources = TherapyResource.objects.filter(is_active=True)[:6]
    
    return render(request, 'therapists/therapists.html', {
        'therapists': therapists,
        'user_sessions': user_sessions,
        'resources': resources,
    })

@login_required
@require_POST
def book_session_view(request):
    therapist_id = request.POST.get('therapist_id')
    therapist = get_object_or_404(Therapist, id=therapist_id)
    session_date = request.POST.get('session_date')
    session_time = request.POST.get('session_time') or None
    notes = request.POST.get('notes', '').strip()
    
    if session_date:
        TherapySession.objects.create(
            user=request.user,
            therapist=therapist,
            session_date=session_date,
            session_time=session_time,
            notes=notes,
            status='scheduled'
        )
        messages.success(request, f"Session request booked with {therapist.name} for {session_date}.")
        
    return redirect('therapists:therapists')

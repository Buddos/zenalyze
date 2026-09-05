from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.crypto import get_random_string
from django.utils import timezone
import json

from .models import (
    CommunityPost, PostComment, PostLike,
    CommunityMessage, AnonymousChatSession, AnonymousMessage, AIChatMessage
)

@login_required
def community_view(request):
    category = request.GET.get('category')
    posts = CommunityPost.objects.filter(status='active')
    
    if category and category != 'all':
        posts = posts.filter(category=category)
        
    user_liked_post_ids = list(
        PostLike.objects.filter(user=request.user).values_list('post_id', flat=True)
    )
    
    return render(request, 'community/community.html', {
        'posts': posts,
        'current_category': category,
        'user_liked_post_ids': user_liked_post_ids,
    })

@login_required
@require_POST
def create_post_view(request):
    title = request.POST.get('title', '').strip()
    content = request.POST.get('content', '').strip()
    category = request.POST.get('category', 'General')
    is_anonymous = 'is_anonymous' in request.POST
    
    if title and content:
        CommunityPost.objects.create(
            user=request.user,
            title=title,
            content=content,
            category=category,
            is_anonymous=is_anonymous
        )
    return redirect('community:community')

@login_required
@require_POST
def add_comment_view(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    content = request.POST.get('content', '').strip()
    is_anonymous = 'is_anonymous' in request.POST
    
    if content:
        PostComment.objects.create(
            post=post,
            user=request.user,
            content=content,
            is_anonymous=is_anonymous
        )
        post.comments_count = post.comments.count()
        post.save(update_fields=['comments_count'])
        
    return redirect(f"/community/#post-{post.id}")

@login_required
@require_POST
def like_post_api(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    like_obj = PostLike.objects.filter(post=post, user=request.user).first()
    
    if like_obj:
        like_obj.delete()
        liked = False
    else:
        PostLike.objects.create(post=post, user=request.user)
        liked = True
        
    count = post.likes.count()
    post.likes_count = count
    post.save(update_fields=['likes_count'])
    
    return JsonResponse({'status': 'ok', 'likes_count': count, 'liked': liked})

@login_required
def chat_messages_api(request):
    # Retrieve messages within last 24h
    cutoff = timezone.now() - timezone.timedelta(hours=24)
    msgs = CommunityMessage.objects.filter(created_at__gte=cutoff).order_by('created_at')[:50]
    
    out = []
    for m in msgs:
        out.append({
            'id': m.id,
            'author': m.user.display_title,
            'message': m.message,
            'is_mine': m.user == request.user,
            'time': m.created_at.strftime('%I:%M %p')
        })
    return JsonResponse({'status': 'ok', 'messages': out})

@login_required
@require_POST
def send_chat_message_api(request):
    try:
        data = json.loads(request.body)
        msg_text = data.get('message', '').strip()
    except Exception:
        msg_text = request.POST.get('message', '').strip()
        
    if msg_text:
        CommunityMessage.objects.create(
            user=request.user,
            message=msg_text,
            message_type='text'
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'Empty message'}, status=400)

@login_required
def anonymous_chat_view(request):
    active_session = AnonymousChatSession.objects.filter(
        status__in=['waiting', 'active']
    ).filter(
        models_q_participant(request.user)
    ).first()
    
    messages = []
    if active_session:
        messages = active_session.messages.order_by('created_at')
        
    return render(request, 'community/anonymous_chat.html', {
        'active_session': active_session,
        'messages': messages,
    })

def models_q_participant(user):
    from django.db.models import Q
    return Q(participant1=user) | Q(participant2=user)

@login_required
@require_POST
def start_anon_chat(request):
    code = get_random_string(6).upper()
    session = AnonymousChatSession.objects.create(
        session_code=code,
        participant1=request.user,
        status='waiting'
    )
    return redirect('community:anonymous_chat')

@login_required
@require_POST
def join_anon_chat(request):
    code = request.POST.get('session_code', '').strip().upper()
    session = AnonymousChatSession.objects.filter(session_code=code, status='waiting').first()
    if session and session.participant1 != request.user:
        session.participant2 = request.user
        session.status = 'active'
        session.save()
    return redirect('community:anonymous_chat')

@login_required
@require_POST
def end_anon_chat(request, session_code):
    session = AnonymousChatSession.objects.filter(session_code=session_code).first()
    if session:
        session.status = 'ended'
        session.ended_at = timezone.now()
        session.save()
    return redirect('community:anonymous_chat')

@login_required
@require_POST
def send_anon_message_api(request, session_code):
    session = get_object_or_404(AnonymousChatSession, session_code=session_code, status='active')
    data = json.loads(request.body)
    text = data.get('message', '').strip()
    if text:
        AnonymousMessage.objects.create(
            session=session,
            user=request.user,
            message_text=text,
            is_anonymous=True
        )
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def poll_anon_messages_api(request, session_code):
    session = get_object_or_404(AnonymousChatSession, session_code=session_code)
    msgs = session.messages.order_by('created_at')
    out = []
    for m in msgs:
        out.append({
            'id': m.id,
            'is_mine': m.user == request.user,
            'text': m.message_text,
            'time': m.created_at.strftime('%I:%M %p')
        })
    return JsonResponse({'status': 'ok', 'messages': out})

@login_required
def ai_chat_view(request):
    return render(request, 'community/ai_chat.html', {'active_nav': 'ai_chat'})

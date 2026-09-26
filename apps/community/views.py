from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.http import require_POST
from django.utils.crypto import get_random_string
from django.utils import timezone
import json

from .models import (
    CommunityPost, MediaAsset, PostMedia, PostComment, PostLike,
    CommunityMessage, AnonymousChatSession, AnonymousMessage, AIChatMessage
)
from apps.administration.models import ContentModeration


def _user_avatar(user):
    try:
        avatar_url = user.avatar_display_url
    except AttributeError:
        avatar_url = None
    try:
        initial = (user.display_title or user.username)[0].upper()
    except AttributeError:
        initial = user.username[0].upper()
    return avatar_url, initial


# ============ COMMUNITY FORUM & CHAT HUB ============

@login_required
def community_view(request):
    category = request.GET.get('category')
    active_tab = request.GET.get('tab', 'discussions')
    posts = (
        CommunityPost.objects
        .filter(status='active', moderation_status='visible')
        .select_related('user')
        .prefetch_related('media_items__media_asset', 'comments__user')
    )
    if category and category != 'all':
        posts = posts.filter(category=category)
    user_liked_post_ids = list(
        PostLike.objects.filter(user=request.user).values_list('post_id', flat=True)
    )

    # Fetch recent community chat messages for embedded Community Chat tab
    cutoff = timezone.now() - timezone.timedelta(hours=48)
    chat_messages = list(
        CommunityMessage.objects
        .filter(created_at__gte=cutoff)
        .select_related('user')
        .order_by('-created_at')[:60]
    )
    chat_messages.reverse()

    recent_active_qs = list(
        CommunityMessage.objects
        .filter(created_at__gte=timezone.now() - timezone.timedelta(minutes=30))
        .values_list('user__username', 'user__id')
        .distinct()[:20]
    )

    return render(request, 'community/community.html', {
        'posts': posts,
        'current_category': category,
        'user_liked_post_ids': user_liked_post_ids,
        'active_nav': 'community',
        'active_tab': active_tab,
        'chat_messages': chat_messages,
        'recent_active_users': recent_active_qs,
        'active_user_count': max(1, len(recent_active_qs)),
    })


@login_required
@require_POST
def create_post_view(request):
    title = request.POST.get('title', '').strip()
    content = request.POST.get('content', '').strip()
    category = request.POST.get('category', 'General')
    is_anonymous = 'is_anonymous' in request.POST
    uploads = request.FILES.getlist('media_files')
    image_extensions = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    video_extensions = {'mp4', 'webm', 'ogv', 'mov'}

    if not content and not uploads:
        messages.error(request, 'Add a reflection or attach media before posting.')
        return redirect('community:community')
    if len(uploads) > 6:
        messages.error(request, 'You can attach up to six images to one post.')
        return redirect('community:community')

    media_types = []
    for upload in uploads:
        extension = upload.name.rsplit('.', 1)[-1].lower() if '.' in upload.name else ''
        if extension in image_extensions:
            media_types.append('image')
            if upload.size > 10 * 1024 * 1024:
                messages.error(request, 'Images must be 10 MB or smaller.')
                return redirect('community:community')
        elif extension in video_extensions:
            media_types.append('video')
            if upload.size > 200 * 1024 * 1024:
                messages.error(request, 'Videos must be 200 MB or smaller.')
                return redirect('community:community')
        else:
            messages.error(request, 'Attach supported image files or MP4, WebM, OGV, or MOV video.')
            return redirect('community:community')

    if media_types and (media_types.count('video') > 1 or ('video' in media_types and len(media_types) > 1)):
        messages.error(request, 'A post can contain up to six images or one video, not both.')
        return redirect('community:community')

    if uploads:
        hour_ago = timezone.now() - timezone.timedelta(hours=1)
        recent_media_posts = CommunityPost.objects.filter(
            user=request.user,
            created_at__gte=hour_ago,
            media_items__isnull=False,
        ).distinct().count()
        if recent_media_posts >= 5:
            messages.error(request, 'You have reached the limit of five media posts per hour.')
            return redirect('community:community')

    with transaction.atomic():
        post = CommunityPost.objects.create(
            user=request.user,
            title=title[:255],
            content=content,
            category=category,
            is_anonymous=is_anonymous,
            moderation_status='pending' if uploads else 'visible',
        )
        for position, (upload, asset_type) in enumerate(zip(uploads, media_types)):
            asset = MediaAsset.objects.create(
                asset_type=asset_type,
                file=upload,
                uploaded_by=request.user,
                processing_status='ready',
            )
            PostMedia.objects.create(post=post, media_asset=asset, position=position)

        if uploads:
            ContentModeration.objects.create(
                content_type='post',
                content_id=post.id,
                reported_by=request.user,
                reason='Community media requires review',
                description=f'{len(uploads)} media attachment(s) are awaiting moderator review.',
            )

    if uploads:
        messages.success(request, 'Your post was submitted and will appear after media review.')
    else:
        messages.success(request, 'Your post has been published.')
    return redirect('community:community')


@login_required
@require_POST
def report_post_view(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id, status='active', moderation_status='visible')
    if post.user_id == request.user.id:
        messages.error(request, 'You cannot report your own post.')
        return redirect(f'/community/#post-{post.id}')

    existing_report = ContentModeration.objects.filter(
        content_type='post',
        content_id=post.id,
        reported_by=request.user,
        status='pending',
    ).exists()
    if not existing_report:
        ContentModeration.objects.create(
            content_type='post',
            content_id=post.id,
            reported_by=request.user,
            reason='Community post reported',
            description=request.POST.get('reason', '').strip()[:2000],
        )
        post.is_reported = True
        post.report_count += 1
        post.save(update_fields=['is_reported', 'report_count'])
        messages.success(request, 'The post was sent to the moderation queue.')
    else:
        messages.info(request, 'You have already reported this post.')
    return redirect(f'/community/#post-{post.id}')


@login_required
@require_POST
def add_comment_view(request, post_id):
    post = get_object_or_404(CommunityPost, id=post_id)
    content = request.POST.get('content', '').strip()
    is_anonymous = 'is_anonymous' in request.POST
    if content:
        PostComment.objects.create(post=post, user=request.user, content=content, is_anonymous=is_anonymous)
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


# ============ COMMUNITY CHAT (PUBLIC LIVE ROOM) ============

@login_required
def live_chat_view(request):
    """Dedicated full-page Community Chat room"""
    cutoff = timezone.now() - timezone.timedelta(hours=48)
    messages = list(
        CommunityMessage.objects
        .filter(created_at__gte=cutoff)
        .select_related('user')
        .order_by('-created_at')[:60]
    )
    messages.reverse()

    recent_active_qs = list(
        CommunityMessage.objects
        .filter(created_at__gte=timezone.now() - timezone.timedelta(minutes=30))
        .values_list('user__username', 'user__id')
        .distinct()[:20]
    )

    return render(request, 'community/live_chat.html', {
        'active_nav': 'community_chat',
        'messages': messages,
        'recent_active_users': recent_active_qs,
        'active_user_count': len(recent_active_qs),
    })


@login_required
def chat_messages_api(request):
    since_id = request.GET.get('since', 0)
    try:
        since_id = int(since_id)
    except (ValueError, TypeError):
        since_id = 0

    if since_id:
        msgs = (
            CommunityMessage.objects
            .filter(id__gt=since_id)
            .select_related('user')
            .order_by('created_at')[:80]
        )
    else:
        cutoff = timezone.now() - timezone.timedelta(hours=48)
        msgs = (
            CommunityMessage.objects
            .filter(created_at__gte=cutoff)
            .select_related('user')
            .order_by('created_at')[:80]
        )

    out = []
    for m in msgs:
        avatar_url, avatar_initial = _user_avatar(m.user)
        out.append({
            'id': m.id,
            'author': m.user.username,
            'username': m.user.username,
            'avatar_url': avatar_url,
            'avatar_initial': avatar_initial,
            'message': m.message,
            'is_mine': m.user == request.user,
            'time': m.created_at.strftime('%I:%M %p'),
            'date': m.created_at.strftime('%b %d'),
            'timestamp': m.created_at.isoformat(),
        })

    last_id = out[-1]['id'] if out else since_id
    return JsonResponse({'status': 'ok', 'messages': out, 'last_id': last_id})


@login_required
@require_POST
def send_chat_message_api(request):
    try:
        data = json.loads(request.body)
        msg_text = data.get('message', '').strip()
    except Exception:
        msg_text = request.POST.get('message', '').strip()

    if not msg_text:
        return JsonResponse({'status': 'error', 'message': 'Empty message'}, status=400)
    if len(msg_text) > 1000:
        return JsonResponse({'status': 'error', 'message': 'Message too long (max 1000 chars)'}, status=400)

    msg = CommunityMessage.objects.create(user=request.user, message=msg_text, message_type='text')
    avatar_url, avatar_initial = _user_avatar(request.user)
    return JsonResponse({
        'status': 'ok',
        'message': {
            'id': msg.id,
            'author': request.user.username,
            'username': request.user.username,
            'avatar_url': avatar_url,
            'avatar_initial': avatar_initial,
            'message': msg.message,
            'is_mine': True,
            'time': msg.created_at.strftime('%I:%M %p'),
            'date': msg.created_at.strftime('%b %d'),
            'timestamp': msg.created_at.isoformat(),
        }
    })


@login_required
def online_users_api(request):
    recent = (
        CommunityMessage.objects
        .filter(created_at__gte=timezone.now() - timezone.timedelta(minutes=5))
        .values('user__id', 'user__username')
        .distinct()[:30]
    )
    users = [{'id': u['user__id'], 'username': u['user__username']} for u in recent]
    return JsonResponse({'status': 'ok', 'online_users': users, 'count': len(users)})


# ============ PRIVATE ANONYMOUS 1-ON-1 CHAT ============

def _q_participant(user):
    from django.db.models import Q
    return Q(participant1=user) | Q(participant2=user)


def models_q_participant(user):
    return _q_participant(user)


ANON_TOPICS = [
    {
        'id': 'Anxiety & Panic',
        'label': 'Anxiety & Panic',
        'icon': '🧠',
        'desc': 'Racing thoughts, panic symptoms, feeling overwhelmed',
        'badge_class': 'bg-primary'
    },
    {
        'id': 'Depression & Low Mood',
        'label': 'Depression & Low Mood',
        'icon': '🌧️',
        'desc': 'Feeling down, lack of motivation, emptiness',
        'badge_class': 'bg-info'
    },
    {
        'id': 'Work & Burnout',
        'label': 'Work & Burnout',
        'icon': '💼',
        'desc': 'Career exhaustion, stress, imposter syndrome',
        'badge_class': 'bg-warning'
    },
    {
        'id': 'Relationships & Heartbreak',
        'label': 'Relationships & Heartbreak',
        'icon': '💔',
        'desc': 'Breakups, loneliness, communication hurt',
        'badge_class': 'bg-danger'
    },
    {
        'id': 'Financial Stress',
        'label': 'Financial Stress',
        'icon': '💸',
        'desc': 'Budget anxiety, debt pressures, uncertainty',
        'badge_class': 'bg-success'
    },
    {
        'id': 'Sleep & Insomnia',
        'label': 'Sleep & Insomnia',
        'icon': '🌙',
        'desc': 'Trouble sleeping, late-night restlessness',
        'badge_class': 'bg-secondary'
    },
    {
        'id': 'Grief & Loss',
        'label': 'Grief & Major Transitions',
        'icon': '🕊️',
        'desc': 'Coping with loss, big life changes',
        'badge_class': 'bg-dark'
    },
    {
        'id': 'General Support',
        'label': 'Just Need to Talk',
        'icon': '🌸',
        'desc': 'A kind listening ear to share how your day went',
        'badge_class': 'bg-primary'
    },
]


@login_required
def anonymous_chat_view(request):
    """100% Private, End-to-End Anonymous 1-on-1 Peer Session with Topic Matching"""
    active_session = (
        AnonymousChatSession.objects
        .filter(status__in=['waiting', 'active'])
        .filter(_q_participant(request.user))
        .first()
    )
    messages = list(active_session.messages.order_by('created_at')) if active_session else []

    is_creator = False
    if active_session:
        is_creator = (request.user == active_session.participant1)

    return render(request, 'community/anonymous_chat.html', {
        'active_session': active_session,
        'messages': messages,
        'is_creator': is_creator,
        'active_nav': 'anonymous_chat',
        'anon_topics': ANON_TOPICS,
    })


@login_required
@require_POST
def match_anon_chat(request):
    """Instant Topic/Issue-Based Matchmaking: pairs peers facing the exact same struggles."""
    topic = request.POST.get('topic', 'General Support').strip() or 'General Support'

    # End any stale sessions for this user first
    AnonymousChatSession.objects.filter(
        status__in=['waiting', 'active']
    ).filter(_q_participant(request.user)).update(status='ended', ended_at=timezone.now())

    cutoff = timezone.now() - timezone.timedelta(minutes=30)
    
    # 1. Look for a waiting peer with the EXACT SAME issue
    waiting_session = (
        AnonymousChatSession.objects
        .filter(status='waiting', created_at__gte=cutoff, participant2__isnull=True, topic__iexact=topic)
        .exclude(participant1=request.user)
        .order_by('created_at')
        .first()
    )

    # 2. Fallback if user selected General Support: match with any waiting peer
    if not waiting_session and topic == 'General Support':
        waiting_session = (
            AnonymousChatSession.objects
            .filter(status='waiting', created_at__gte=cutoff, participant2__isnull=True)
            .exclude(participant1=request.user)
            .order_by('created_at')
            .first()
        )

    if waiting_session:
        waiting_session.participant2 = request.user
        waiting_session.status = 'active'
        waiting_session.save()
    else:
        # Create a new private room waiting for a peer with this exact issue
        code = get_random_string(6).upper()
        AnonymousChatSession.objects.create(
            session_code=code,
            participant1=request.user,
            status='waiting',
            topic=topic
        )

    return redirect('community:anonymous_chat')


@login_required
@require_POST
def start_anon_chat(request):
    """Create a private room with a shared 6-character room code and specified topic."""
    topic = request.POST.get('topic', 'General Support').strip() or 'General Support'
    AnonymousChatSession.objects.filter(
        status__in=['waiting', 'active']
    ).filter(_q_participant(request.user)).update(status='ended', ended_at=timezone.now())
    code = get_random_string(6).upper()
    AnonymousChatSession.objects.create(
        session_code=code,
        participant1=request.user,
        status='waiting',
        topic=topic
    )
    return redirect('community:anonymous_chat')


@login_required
@require_POST
def join_anon_chat(request):
    """Join a private room by code."""
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
    """End private session. Securely wipes messages if requested for total privacy."""
    session = AnonymousChatSession.objects.filter(session_code=session_code).first()
    if session and (request.user == session.participant1 or request.user == session.participant2):
        # Optional purge for zero trace privacy
        purge = request.POST.get('purge') == '1' or request.GET.get('purge') == '1'
        if purge:
            session.messages.all().delete()
        session.status = 'ended'
        session.ended_at = timezone.now()
        session.save()
    return redirect('community:anonymous_chat')


@login_required
@require_POST
def send_anon_message_api(request, session_code):
    """Send message in private anonymous room with participant validation."""
    session = get_object_or_404(AnonymousChatSession, session_code=session_code)
    
    # Strict privacy verification: only the two assigned peers can communicate
    if request.user != session.participant1 and request.user != session.participant2:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
        
    if session.status != 'active':
        return JsonResponse({'status': 'error', 'message': 'Session is not active yet or has ended'}, status=400)

    try:
        data = json.loads(request.body)
    except Exception:
        data = {}
    text = data.get('message', '').strip()
    if text:
        if len(text) > 1000:
            return JsonResponse({'status': 'error', 'message': 'Message too long (max 1000 chars)'}, status=400)

        msg = AnonymousMessage.objects.create(
            session=session, user=request.user, message_text=text, is_anonymous=True
        )
        return JsonResponse({
            'status': 'ok',
            'message': {
                'id': msg.id,
                'is_mine': True,
                'text': msg.message_text,
                'time': msg.created_at.strftime('%I:%M %p')
            }
        })
    return JsonResponse({'status': 'error', 'message': 'Empty message'}, status=400)


@login_required
def poll_anon_messages_api(request, session_code):
    """Private message polling: guarantees no user identity leaks & returns issue topic."""
    try:
        session = AnonymousChatSession.objects.get(session_code=session_code)
    except AnonymousChatSession.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Session not found'}, status=404)

    # Privacy verification: only participants are permitted to poll
    if request.user != session.participant1 and request.user != session.participant2:
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)

    since_id = request.GET.get('since', 0)
    try:
        since_id = int(since_id)
    except (ValueError, TypeError):
        since_id = 0

    msgs_qs = (
        session.messages.filter(id__gt=since_id).order_by('created_at')
        if since_id else
        session.messages.order_by('created_at')
    )

    out = [
        {
            'id': m.id,
            'is_mine': m.user == request.user,
            'text': m.message_text,
            'time': m.created_at.strftime('%I:%M %p')
        }
        for m in msgs_qs
    ]

    return JsonResponse({
        'status': 'ok',
        'messages': out,
        'session_status': session.status,
        'has_peer': session.participant2 is not None,
        'topic': session.topic,
        'last_id': out[-1]['id'] if out else since_id,
    })


@login_required
def ai_chat_view(request):
    return render(request, 'community/ai_chat.html', {'active_nav': 'ai_chat'})

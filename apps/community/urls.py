from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('community/', views.community_view, name='community'),
    path('community/', views.community_view, name='index'),
    path('community/post/create/', views.create_post_view, name='create_post'),
    path('community/post/<int:post_id>/report/', views.report_post_view, name='report_post'),
    path('community/post/<int:post_id>/comment/', views.add_comment_view, name='add_comment'),
    path('community/like/<int:post_id>/', views.like_post_api, name='like_post'),
    path('community/chat/', views.live_chat_view, name='community_chat'),
    path('community/chat/', views.live_chat_view, name='live_chat'),
    path('community/chat/messages/', views.chat_messages_api, name='chat_messages'),
    path('community/chat/send/', views.send_chat_message_api, name='send_chat_message'),
    path('community/chat/online-users/', views.online_users_api, name='online_users'),
    path('anonymous-chat/', views.anonymous_chat_view, name='anonymous_chat'),
    path('anonymous-chat/match/', views.match_anon_chat, name='match_anon_chat'),
    path('anonymous-chat/start/', views.start_anon_chat, name='start_anon_chat'),
    path('anonymous-chat/join/', views.join_anon_chat, name='join_anon_chat'),
    path('anonymous-chat/<str:session_code>/end/', views.end_anon_chat, name='end_anon_chat'),
    path('anonymous-chat/<str:session_code>/send/', views.send_anon_message_api, name='send_anon_message'),
    path('anonymous-chat/<str:session_code>/poll/', views.poll_anon_messages_api, name='poll_anon_messages'),
    path('ai-chat/', views.ai_chat_view, name='ai_chat'),
]

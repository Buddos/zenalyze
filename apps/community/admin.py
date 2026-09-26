from django.contrib import admin
from .models import (
    CommunityPost,
    MediaAsset,
    PostComment,
    PostLike,
    CommunityMessage,
    AnonymousChatSession,
    AnonymousMessage,
    AIChatMessage,
)


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'status', 'moderation_status', 'is_pinned', 'likes_count', 'comments_count', 'created_at')
    list_filter = ('status', 'moderation_status', 'category', 'is_pinned', 'is_anonymous', 'created_at')
    search_fields = ('title', 'content', 'user__username')


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = ('id', 'asset_type', 'file', 'processing_status', 'uploaded_by', 'created_at')
    list_filter = ('asset_type', 'processing_status', 'created_at')
    search_fields = ('file', 'uploaded_by__username')
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        if not obj.uploaded_by_id:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(PostComment)
class PostCommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'is_anonymous', 'created_at')
    list_filter = ('is_anonymous', 'created_at')
    search_fields = ('content', 'user__username', 'post__title')


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    search_fields = ('user__username', 'post__title')


@admin.register(CommunityMessage)
class CommunityMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'message_type', 'created_at')
    list_filter = ('message_type', 'created_at')
    search_fields = ('message', 'user__username')


@admin.register(AnonymousChatSession)
class AnonymousChatSessionAdmin(admin.ModelAdmin):
    list_display = ('session_code', 'participant1', 'participant2', 'status', 'created_at', 'ended_at')
    list_filter = ('status', 'created_at')
    search_fields = ('session_code', 'participant1__username', 'participant2__username')


@admin.register(AnonymousMessage)
class AnonymousMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'user', 'is_anonymous', 'created_at')
    list_filter = ('is_anonymous', 'created_at')
    search_fields = ('message_text', 'session__session_code', 'user__username')


@admin.register(AIChatMessage)
class AIChatMessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'message')

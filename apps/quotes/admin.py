from django.contrib import admin
from .models import Quote, QuoteUserInteraction, DailyQuoteView


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('quote_text_short', 'author', 'category', 'language', 'is_featured', 'is_active', 'created_at')
    list_filter = ('category', 'language', 'is_featured', 'is_active')
    search_fields = ('quote_text', 'author', 'category')

    def quote_text_short(self, obj):
        return obj.quote_text[:50] + ('...' if len(obj.quote_text) > 50 else '')
    quote_text_short.short_description = 'Quote'


@admin.register(QuoteUserInteraction)
class QuoteUserInteractionAdmin(admin.ModelAdmin):
    list_display = ('user', 'quote', 'is_favorite', 'is_viewed', 'created_at')
    list_filter = ('is_favorite', 'is_viewed', 'created_at')
    search_fields = ('user__username', 'quote__quote_text', 'quote__author')


@admin.register(DailyQuoteView)
class DailyQuoteViewAdmin(admin.ModelAdmin):
    list_display = ('user', 'quote', 'viewed_at')
    list_filter = ('viewed_at',)
    search_fields = ('user__username', 'quote__quote_text')

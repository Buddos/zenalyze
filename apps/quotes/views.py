from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Quote, QuoteUserInteraction

@login_required
def quotes_view(request):
    user = request.user
    category = request.GET.get('category')
    fav_only = request.GET.get('favorite') == 'true'
    
    quotes_qs = Quote.objects.filter(is_active=True)
    
    if category and category != 'all':
        quotes_qs = quotes_qs.filter(category=category)
        
    user_fav_ids = list(
        QuoteUserInteraction.objects.filter(user=user, is_favorite=True).values_list('quote_id', flat=True)
    )
    
    if fav_only:
        quotes_qs = quotes_qs.filter(id__in=user_fav_ids)
        
    # Categories list
    categories = Quote.objects.filter(is_active=True).values_list('category', flat=True).distinct().order_by('category')
    
    # Featured / daily quote
    featured_quote = Quote.objects.filter(is_featured=True).first()
    if not featured_quote:
        featured_quote = Quote.objects.filter(is_active=True).first()
        
    paginator = Paginator(quotes_qs, 21)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'quotes/quotes.html', {
        'page_obj': page_obj,
        'categories': categories,
        'current_category': category,
        'is_favorite_filter': fav_only,
        'user_fav_ids': user_fav_ids,
        'featured_quote': featured_quote,
        'total_count': Quote.objects.filter(is_active=True).count(),
    })

@login_required
@require_POST
def toggle_favorite_api(request, quote_id):
    quote = get_object_or_404(Quote, id=quote_id)
    inter, created = QuoteUserInteraction.objects.get_or_create(user=request.user, quote=quote)
    inter.is_favorite = not inter.is_favorite
    inter.save(update_fields=['is_favorite'])
    return JsonResponse({'status': 'ok', 'is_favorite': inter.is_favorite})

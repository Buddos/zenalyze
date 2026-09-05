from django.shortcuts import render, redirect
from django.contrib import messages
from apps.administration.models import TeamMember, ContactMessage, CrisisResource
from apps.quotes.models import Quote

def index_view(request):
    if request.user.is_authenticated:
        return redirect('wellness:dashboard')
    
    quote = Quote.objects.filter(is_active=True).order_by('?').first()
    team_members = TeamMember.objects.filter(status='active').order_by('display_order')[:4]
    
    context = {
        'quote': quote,
        'team_members': team_members,
    }
    return render(request, 'core/index.html', context)

def about_view(request):
    team_members = TeamMember.objects.filter(status='active').order_by('display_order')
    return render(request, 'core/about.html', {'team_members': team_members})

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()
        
        if name and email and message:
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            messages.success(request, 'Thank you! Your message has been sent successfully. We will be in touch shortly.')
            return redirect('core:contact')
        else:
            messages.error(request, 'Please fill in all required fields.')
            
    return render(request, 'core/contact.html')

def terms_view(request):
    return render(request, 'core/terms.html')

def privacy_view(request):
    return render(request, 'core/privacy.html')

def help_view(request):
    return render(request, 'core/help.html')

def crisis_help_view(request):
    resources = CrisisResource.objects.filter(is_active=True).order_by('-priority')
    return render(request, 'core/crisis_help.html', {'resources': resources})

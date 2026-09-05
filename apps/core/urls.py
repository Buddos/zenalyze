from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('home/', views.index_view, name='home'),
    path('', views.index_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('help-center/', views.help_view, name='help'),
    path('support/', views.help_view, name='support'),
    path('crisis-help/', views.crisis_help_view, name='crisis_help'),
]

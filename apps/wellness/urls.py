from django.urls import path
from . import views
from apps.core import views as core_views

app_name = 'wellness'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('mood-log/', views.mood_log_view, name='mood_log'),
    path('journal/', views.journal_view, name='journal'),
    path('journal/favorite/<int:entry_id>/', views.toggle_journal_favorite, name='toggle_journal_favorite'),
    path('exercises/', views.exercises_view, name='exercises'),
    path('exercises/complete/<int:exercise_id>/', views.complete_exercise_api, name='complete_exercise'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('history/', views.history_view, name='history'),
    path('financial/', views.financial_view, name='financial'),
    path('financial-planner/', views.financial_view, name='financial_planner'),
    path('relationships/', views.relationships_view, name='relationships'),
    path('motivations/', views.motivations_view, name='motivations'),
    path('motivations/complete/<int:motivation_id>/', views.complete_motivation_view, name='complete_motivation'),
    path('generate-report/', views.generate_report_view, name='generate_report'),
    path('generate-report/', views.generate_report_view, name='report'),
    path('crisis-help/', core_views.crisis_help_view, name='crisis_help'),
]

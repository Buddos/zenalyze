from django.urls import path
from . import views

app_name = 'therapists'

urlpatterns = [
    path('therapy/', views.therapists_view, name='therapists'),
    path('therapy/', views.therapists_view, name='index'),
    path('therapists/', views.therapists_view, name='therapists_alias'),
    path('therapy/book/', views.book_session_view, name='book_session'),
]

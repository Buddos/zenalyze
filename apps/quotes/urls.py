from django.urls import path
from . import views

app_name = 'quotes'

urlpatterns = [
    path('quotes/', views.quotes_view, name='quotes'),
    path('quotes/', views.quotes_view, name='index'),
    path('quotes/favorite/<int:quote_id>/', views.toggle_favorite_api, name='toggle_favorite'),
]

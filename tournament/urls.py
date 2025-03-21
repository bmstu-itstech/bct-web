from django.urls import path

from . import views

urlpatterns = [
    path('games/<game_id>/', views.leaderboard, name='leaderboard'),
    path('games/<game_id>/upload', views.upload, name='upload'),
    path('games/<game_id>/rules/', views.rules, name='rules'),
    path('', views.home, name='home'),
]

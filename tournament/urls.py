from django.urls import path

from . import views

urlpatterns = [
    path('games/<game_id>/', views.leaderboard, name='leaderboard'),
    path('games/upload/<game_id>/', views.upload, name='upload'),
    path('', views.home, name='home'),
]

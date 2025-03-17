from django.urls import path

from . import views

urlpatterns = [
    path('', views.leaderboard, name='leaderboard'),
    path('upload/', views.upload, name='upload'),
]

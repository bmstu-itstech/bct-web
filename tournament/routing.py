from django.urls import path

from tournament import consumers


websocket_urlpatterns = [
    path('ws/leaderboard/', consumers.LeaderboardConsumer.as_asgi()),
]

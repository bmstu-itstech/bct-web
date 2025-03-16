from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required(login_url='/auth/login')
def leaderboard(request):
    return render(request, 'tournament/leaderboard.html')

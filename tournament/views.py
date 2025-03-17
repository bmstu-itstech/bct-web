from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from tournament import models
from tournament.models import Team

@login_required(login_url='/auth/login')
def leaderboard(request, game_id):
    user = User.objects.get(username=request.user.username)
    team = Team.objects.get(user=user)
    game = models.Game.objects.get(id=game_id)
    if not game:
        return HttpResponse('no game found', status=404)
    program = team.last_program(game_id)
    if program:
        return render(
            request,
            'tournament/leaderboard.html',
            context={
                        'game': game,
                        'program_name': program.file.name.split('/')[-1],
                        'program_url': program.file.url,
                    }
        )
    return render(
        request,
        'tournament/leaderboard.html',
        context={
                    'game': game,
                }
    )


@login_required(login_url='/auth/login')
@require_http_methods(['POST'])
def upload(request, game_id):
    user = request.user
    uploaded_file = request.FILES.get('file')
    if uploaded_file is None:
        return HttpResponse('expected file\n', status=400)
    user = User.objects.get(username=user.username)
    team = Team.objects.get(user=user)
    game = models.Game.objects.get(id=game_id)
    program = models.Program.objects.create(game=game, team=team, file=uploaded_file)
    program.save()
    return redirect(request.META.get('HTTP_REFERER'))


def home(request):
    return redirect('games/1/')

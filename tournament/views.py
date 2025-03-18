import markdown
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from tournament import models
from tournament.models import Team, Player


@login_required(login_url='/auth/login')
def leaderboard(request, game_id):
    user = User.objects.get(username=request.user.username)
    player = Player.objects.get(user=user)
    team = player.team
    game = models.Game.objects.get(id=game_id)
    if not game:
        return HttpResponse('no game found', status=404)
    program = team.last_program(game_id)
    if program:
        return render(
            request,
            'tournament/leaderboard.html',
            context={
                        'games': list(models.Game.objects.all()),
                        'current_game': game,
                        'program_name': program.file.name.split('/')[-1],
                        'program_url': program.file.url,
                    }
        )
    return render(
        request,
        'tournament/leaderboard.html',
        context={
                    'games': list(models.Game.objects.all()),
                    'current_game': game,
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
    player = Player.objects.get(user=user)
    team = player.team
    game = models.Game.objects.get(id=game_id)
    program = models.Program.objects.create(game=game, team=team, file=uploaded_file)
    program.save()
    return redirect(request.META.get('HTTP_REFERER'))


def rules(request, game_id):
    game = models.Game.objects.get(id=game_id)
    html_content = markdown.markdown(
        game.description,
        extensions=[
            'markdown.extensions.codehilite',
            'markdown.extensions.fenced_code',
        ]
    )
    return render(
        request,
        'tournament/rules.html',
        context={
                    'content': html_content,
                    'games': list(models.Game.objects.all()),
                    'current_game': game,
                }
    )

def home(request):
    first_game = models.Game.objects.first()
    return redirect(f'games/{first_game.id}/')

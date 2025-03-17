from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from tournament import models
from tournament.models import Team


@login_required(login_url='/auth/login')
def leaderboard(request):
    user = User.objects.get(username=request.user.username)
    team = Team.objects.get(user=user)
    program = team.last_program()
    if program:
        return render(
            request,
            'tournament/leaderboard.html',
            context={
                        'game': 'Дилемма заключенного',
                        'program_name': program.file.name.split('/')[-1],
                        'program_url': program.file.url,
                    }
        )
    return render(
        request,
        'tournament/leaderboard.html',
        context={
                    'game': 'Дилемма заключенного',
                }
    )


@login_required(login_url='/auth/login')
@require_http_methods(['POST'])
def upload(request):
    user = request.user
    uploaded_file = request.FILES.get('file')
    if uploaded_file is None:
        return HttpResponse('expected file\n', status=400)
    user = User.objects.get(username=user.username)
    team = Team.objects.get(user=user)
    program = models.Program.objects.create(team=team, file=uploaded_file)
    program.save()
    return redirect('/')

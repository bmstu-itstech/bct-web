import subprocess
import sys
from itertools import combinations

from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer

from django.conf import settings
from django.db import models
from django.db.models import Q, Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver, Signal


class Team(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team',
        related_query_name='team'
    )

    def last_program(self, game_id):
        game = Game.objects.get(id=game_id)
        return (self.programs
                .filter(game=game)
                .order_by('uploaded_at')
                .last())

    def score(self, game_id):
        program = self.last_program(game_id)
        if program is None:
            return 0
        tour = Tour.last_tour(game_id)
        if tour is None:
            return 0
        res = Result.objects.filter(
            program=program,
            round__tour=tour,
        ).aggregate(Sum('score', default=-1))['score__sum']
        return res

    def __str__(self):
        return self.user.username


class Program(models.Model):
    game = models.ForeignKey(
        'Game',
        on_delete=models.CASCADE,
        related_name='programs',
    )
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='programs',
    )
    file = models.FileField(
        upload_to='programs/%Y/%m/%d/%H/%M',
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'{self.team}: {self.file}'


class Game(models.Model):
    name = models.CharField(
        max_length=127,
        unique=True
    )

    def __str__(self):
        return self.name


class Tour(models.Model):
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='tours',
    )
    played_at = models.DateTimeField(
        auto_now_add=True
    )

    @classmethod
    def last_tour(cls, game_id):
        game = Game.objects.get(id=game_id)
        return cls.objects.filter(game=game).order_by('played_at').last()

    def __str__(self):
        return f'{self.game.name}: {self.played_at}'


class Round(models.Model):
    tour = models.ForeignKey(
        Tour,
        on_delete=models.CASCADE,
        related_name='rounds',
    )
    left = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='played_as_left',
    )
    right = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='played_as_right',
    )
    played_at = models.DateTimeField(
        auto_now_add=True
    )

    @classmethod
    def last_rounds(cls, game_id, program):
        last_tour = Tour.last_tour(game_id)
        if last_tour is None:
            return None
        return (
            last_tour
                .rounds
                .filter(Q(left=program) | Q(right=program))
        )

    def __str__(self):
        return f'{self.tour.game}: {self.left} vs {self.right}'


class Result(models.Model):
    round = models.ForeignKey(
        Round,
        on_delete=models.CASCADE,
        related_name='results',
    )
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name='results',
    )
    score = models.IntegerField()
    error = models.CharField(
        blank=True,
        max_length=255,
    )

    def __str__(self):
        if self.error:
            return f'{self.program}: {self.error}'
        return f'{self.program}: {self.score}'


def fetch_team_results_sync(game_id):
    teams = list(Team.objects.all())
    results = [
        {
            'name': team.user.username,
            'score': team.score(game_id),
        }
        for team in teams
    ]
    results.sort(key=lambda team: team['score'], reverse=True)
    return results


fetch_team_results_async = sync_to_async(fetch_team_results_sync)


@receiver(post_save, sender=Result)
@receiver(post_delete, sender=Result)
def send_update(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    results = fetch_team_results_sync(instance.program.game.id)
    async_to_sync(channel_layer.group_send)(
        'results_updates',
        {
            'type': 'send_results_update',
            'results': results,
        },
    )


JUDGE = './bct-judge'

@receiver(post_save, sender=Program)
@receiver(post_delete, sender=Program)
def play(sender, instance, **kwargs):
    game = instance.game
    teams = list(Team.objects.all())
    programs = []
    for team in teams:
        program = team.last_program(game.id)
        if program:
            programs.append(program)

    tour = Tour.objects.create(game=game)

    for pl, pr in combinations(programs, 2):
        rnd = Round.objects.create(tour=tour, left=pl, right=pr)
        r = subprocess.run(args=[JUDGE, 'dilemma', pl.file.path, pr.file.path], capture_output=True, text=True)
        if r.returncode != 0:
            print(r.stderr, file=sys.stderr)
        else:
            left_score, right_score = map(int, r.stdout.split())
            Result.objects.create(round=rnd, program=pl, score=left_score)
            Result.objects.create(round=rnd, program=pr, score=right_score)

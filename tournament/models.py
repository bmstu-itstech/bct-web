from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
from django.conf import settings
from django.db import models
from django.db.models import Q, Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Team(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='team',
        related_query_name='team'
    )

    def last_program(self):
        return self.programs.order_by('uploaded_at').last()

    def score(self):
        program = self.last_program()
        if program is None:
            return 0
        tour = Tour.last_tour()
        if tour is None:
            return 0
        return Result.objects.filter(
            program=program,
            round__tour=tour,
        ).aggregate(Sum('score'))['score__sum']

    def __str__(self):
        return self.user.username


class Program(models.Model):
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
    def last_tour(cls):
        return cls.objects.order_by('played_at').last()

    def __str__(self):
        return '{}: {}' % self.game.id, self.game.name


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
    def last_rounds(cls, program_id):
        last_tour = Tour.last_tour()
        if last_tour is None:
            return None
        return (
            last_tour
                .rounds
                .filter(Q(left_id=program_id) | Q(right_id=program_id))
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
        null=True,
        max_length=255,
    )

    def __str__(self):
        if self.error:
            return f'{self.program}: {self.error}'
        return f'{self.program}: {self.score}'


def fetch_team_results_sync():
    teams = list(Team.objects.all())
    results = [
        {
            "name": team.user.username,
            "score": team.score(),
        }
        for team in teams
    ]
    results.sort(key=lambda team: team["score"], reverse=True)
    return results

fetch_team_results_async = sync_to_async(fetch_team_results_sync)


@receiver(post_save, sender=Team)
@receiver(post_delete, sender=Team)
def send_update(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    results = fetch_team_results_sync()
    async_to_sync(channel_layer.group_send)(
        'results_updates',
        {
            'type': 'send_results_update',
            'results': results,
        },
    )

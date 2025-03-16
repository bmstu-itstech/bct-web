from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.name


@receiver(post_save, sender=Team)
@receiver(post_delete, sender=Team)
def send_update(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    teams = Team.objects.all().order_by('-score')
    results = [{"name": team.name, "score": team.score} for team in teams]
    async_to_sync(channel_layer.group_send)(
        "results_updates",
        {
            "type": "send_results_update",
            "results": results,
        },
    )

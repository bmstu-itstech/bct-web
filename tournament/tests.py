from datetime import datetime, timedelta
from django.test import TestCase

from tournament import models


class TeamTestCase(TestCase):
    def setUp(self):
        self.team_a = models.Team.objects.create(name='A')
        self.team_b = models.Team.objects.create(name='B')
        self.team_c = models.Team.objects.create(name='C')
        p1o = models.Program.objects.create(
            team=self.team_a,
            file='main1o.py',
            uploaded_at=datetime.now(),
        )
        p1 = models.Program.objects.create(
            team=self.team_a,
            file='main1.py',
            uploaded_at=datetime.now() + timedelta(minutes=1),
        )
        p2 = models.Program.objects.create(
            team=self.team_b,
            file='main2.py',
            uploaded_at=datetime.now(),
        )
        p3 = models.Program.objects.create(
            team=self.team_c,
            file='main3.py',
            uploaded_at=datetime.now(),
        )

        game = models.Game.objects.create(name='Game 1')
        tour1 = models.Tour.objects.create(game=game)

        round1 = models.Round.objects.create(
            tour=tour1,
            left=p1,
            right=p2,
        )
        round2 = models.Round.objects.create(
            tour=tour1,
            left=p2,
            right=p3,
        )
        round3 = models.Round.objects.create(
            tour=tour1,
            left=p3,
            right=p1,
        )

        models.Result.objects.create(
            round=round1,
            program=p1,
            score=10,
        )
        models.Result.objects.create(
            round=round1,
            program=p2,
            score=11,
        )
        models.Result.objects.create(
            round=round2,
            program=p2,
            score=20,
        )
        models.Result.objects.create(
            round=round2,
            program=p3,
            score=23,
        )
        models.Result.objects.create(
            round=round3,
            program=p3,
            score=30,
        )
        models.Result.objects.create(
            round=round3,
            program=p1,
            score=33,
        )

    def test_last_program(self):
        self.assertEqual(
            self.team_a.last_program().file,
            'main1.py'
        )

    def test_score_of_command_a(self):
        self.assertEqual(self.team_a.score(), 10 + 33)

    def test_score_of_command_b(self):
        self.assertEqual(self.team_b.score(), 11 + 20)

    def test_score_of_command_c(self):
        self.assertEqual(self.team_c.score(), 23 + 30)

from django.contrib import admin

from tournament import models


@admin.register(models.Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
    ]


@admin.register(models.Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'game',
        'team',
        'file',
        'uploaded_at',
    ]


@admin.register(models.Game)
class GameAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'name',
    ]


@admin.register(models.Tour)
class TourAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'game',
        'played_at',
    ]


@admin.register(models.Round)
class RoundAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'tour',
        'left',
        'right',
        'played_at',
    ]


@admin.register(models.Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'round',
        'program',
        'score',
        'error',
    ]

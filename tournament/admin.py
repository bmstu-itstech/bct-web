from django.contrib import admin

from tournament import models


admin.site.register(models.Team)
admin.site.register(models.Program)
admin.site.register(models.Game)
admin.site.register(models.Tour)
admin.site.register(models.Round)
admin.site.register(models.Result)

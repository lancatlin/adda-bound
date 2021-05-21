from django.contrib import admin
from core import models


class RoomAdmin(admin.ModelAdmin):
    model = models.Room
    filter_horizontal = ('rooms',)


admin.site.register(models.Room, RoomAdmin)
admin.site.register(models.Pairing)

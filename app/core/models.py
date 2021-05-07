from django.utils.translation import gettext_lazy as _
from django.db import models


class Room(models.Model):
    '''Room is the basic unit in a chat, could be one or group'''

    class Service(models.TextChoices):
        LINE = 'LN', _('LINE')
        MESSENGER = 'MS', _('Messenger')
        TELEGRAM = 'TG', _('Telegram')
        DISCORD = 'DC', _('Discord')

    room_id = models.CharField(max_length=255)
    service = models.CharField(choices=Service.choices, max_length=2)
    name = models.CharField(max_length=255)
    rooms = models.ManyToManyField('self', symmetrical=True)

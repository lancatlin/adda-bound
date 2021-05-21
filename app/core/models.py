from django.db import models
from django.utils.translation import gettext_lazy as _


class Room(models.Model):
    '''Room is the basic unit in a chat, could be one or group'''

    class Service(models.TextChoices):
        LINE = 'LN', _('LINE')
        MESSENGER = 'MS', _('Messenger')
        TELEGRAM = 'TG', _('Telegram')
        DISCORD = 'DC', _('Discord')

    class RoomType(models.TextChoices):
        USER = 'U', _('User')
        Group = 'G', _('Group')
        Room = 'R', _('Room')

    room_id = models.CharField(max_length=255)
    room_type = models.CharField(choices=RoomType.choices, max_length=1)
    service = models.CharField(choices=Service.choices, max_length=2)
    name = models.CharField(max_length=255)
    rooms = models.ManyToManyField('self', symmetrical=True)

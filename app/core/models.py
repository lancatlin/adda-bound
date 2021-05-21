import random

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
        GROUP = 'G', _('Group')
        ROOM = 'R', _('Room')

    room_id = models.CharField(max_length=255)
    room_type = models.CharField(choices=RoomType.choices, max_length=1)
    service = models.CharField(choices=Service.choices, max_length=2)
    name = models.CharField(max_length=255)
    rooms = models.ManyToManyField('self', symmetrical=True)

    def __str__(self):
        return self.name


def random_token():
    while True:
        token = random.randrange(100000, 1000000)
        if not Pairing.objects.filter(token=token).exists():
            return token


class Pairing(models.Model):
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name='pairings',
    )
    token = models.IntegerField(default=random_token)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.room.name} - {self.token}'

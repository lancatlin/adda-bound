from django.db import models


class Room(models.Model):
    LINE = 'LINE'
    MESSENGER = 'MSG'
    TELEGRAM = 'TG'
    SERVICES = (
        (LINE, 'LINE'),
        (MESSENGER, 'Messenger'),
        (TELEGRAM, 'Telegram'),
    )

    room_id = models.CharField(max_length=64)
    name = models.CharField(max_length=64)
    service = models.CharField(max_length=64, choices=SERVICES)
    paired_rooms = models.ManyToManyField("self")

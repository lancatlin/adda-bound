from django.test import TestCase
from core.models import Room


def sample_room(**kwargs):
    payload = {
        'room_id': '1234567',
        'room_type': Room.RoomType.USER,
        'service': Room.Service.LINE,
        'name': 'test',
    }
    payload.update(**kwargs)
    return Room.objects.create(**payload)


class RoomTests(TestCase):
    def test_create_rooms(self):
        '''Test creating rooms and add each other to rooms'''
        room1 = sample_room(name='room1')
        room2 = sample_room(name='room2')
        room1.rooms.add(room2)
        self.assertEqual(room1.rooms.count(), 1)
        self.assertEqual(room2.rooms.get(name=room1.name), room1)

    def test_create_rooms_and_not_add_eachother(self):
        room1 = sample_room(name='room1')
        room2 = sample_room(name='room2')
        self.assertEqual(room1.rooms.count(), 0)
        self.assertEqual(room2.rooms.count(), 0)

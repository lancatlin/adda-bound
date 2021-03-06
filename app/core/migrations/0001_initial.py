# Generated by Django 3.2.3 on 2021-05-21 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_id', models.CharField(max_length=255)),
                ('room_type', models.CharField(choices=[('U', 'User'), ('G', 'Group'), ('R', 'Room')], max_length=1)),
                ('service', models.CharField(choices=[('LN', 'LINE'), ('MS', 'Messenger'), ('TG', 'Telegram'), ('DC', 'Discord')], max_length=2)),
                ('name', models.CharField(max_length=255)),
                ('rooms', models.ManyToManyField(related_name='_core_room_rooms_+', to='core.Room')),
            ],
        ),
    ]

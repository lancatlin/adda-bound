# Generated by Django 3.2.3 on 2021-05-21 10:37

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_pairing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pairing',
            name='token',
            field=models.IntegerField(default=core.models.random_token),
        ),
    ]
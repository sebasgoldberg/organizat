# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('planificacion', '0002_auto_20150410_2250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cronograma',
            name='fecha_inicio',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 11, 16, 26, 57, 936968, tzinfo=utc), null=True, verbose_name='Fecha de inicio', blank=True),
        ),
    ]

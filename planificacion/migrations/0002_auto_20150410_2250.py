# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('planificacion', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cronograma',
            name='fecha_inicio',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 10, 22, 50, 56, 285233, tzinfo=utc), null=True, verbose_name='Fecha de inicio', blank=True),
        ),
    ]

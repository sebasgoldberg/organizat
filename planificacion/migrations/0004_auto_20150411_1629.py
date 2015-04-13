# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('planificacion', '0003_auto_20150411_1626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cronograma',
            name='fecha_inicio',
            field=models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Fecha de inicio', blank=True),
        ),
    ]

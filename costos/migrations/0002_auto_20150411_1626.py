# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('costos', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='costocronograma',
            name='cronograma',
            field=models.OneToOneField(editable=False, to='planificacion.Cronograma', verbose_name='Cronograma'),
        ),
        migrations.AlterField(
            model_name='costointervalo',
            name='intervalo',
            field=models.OneToOneField(editable=False, to='planificacion.IntervaloCronograma', verbose_name='Intervalo'),
        ),
    ]

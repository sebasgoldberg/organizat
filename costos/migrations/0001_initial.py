# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('produccion', '0001_initial'),
        ('planificacion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CostoCronograma',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('costo', models.DecimalField(default=0, verbose_name='Costo ($)', editable=False, max_digits=12, decimal_places=3)),
                ('cronograma', models.ForeignKey(editable=False, to='planificacion.Cronograma', unique=True, verbose_name='Cronograma')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CostoIntervalo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('costo', models.DecimalField(default=0, verbose_name='Costo ($)', editable=False, max_digits=12, decimal_places=3)),
                ('intervalo', models.ForeignKey(editable=False, to='planificacion.IntervaloCronograma', unique=True, verbose_name='Intervalo')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CostoMaquina',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('costo_por_hora', models.DecimalField(default=0, help_text='Costo de utilizaci\xf3n de la m\xe1quina por hora.', verbose_name='Costo ($/h)', max_digits=12, decimal_places=3)),
                ('maquina', models.ForeignKey(editable=False, to='produccion.Maquina', verbose_name='Maquina')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Calendario',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExcepcionLaborable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fecha', models.DateField(verbose_name='Fecha')),
                ('hora_desde', models.TimeField(verbose_name='Hora desde')),
                ('hora_hasta', models.TimeField(verbose_name='Hora hasta')),
                ('laborable', models.BooleanField(default=False, help_text='Indica si la excepci\xf3n es laborable o no laborable.', verbose_name='Laborable')),
                ('calendario', models.ForeignKey(verbose_name='Calendario', to='calendario.Calendario')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IntervaloLaborable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dia', models.IntegerField(verbose_name='D\xeda', choices=[(0, 'Lunes'), (1, 'Martes'), (2, 'Mi\xe9rcoles'), (3, 'Jueves'), (4, 'Viernes'), (5, 'S\xe1bado'), (6, 'Domingo')])),
                ('hora_desde', models.TimeField(verbose_name='Hora desde')),
                ('hora_hasta', models.TimeField(verbose_name='Hora hasta')),
                ('calendario', models.ForeignKey(verbose_name='Calendario', to='calendario.Calendario')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]

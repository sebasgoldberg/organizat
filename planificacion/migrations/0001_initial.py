# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('produccion', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cronograma',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descripcion', models.CharField(max_length=100, verbose_name='Descripci\xf3n')),
                ('fecha_inicio', models.DateTimeField(default=datetime.datetime(2015, 4, 10, 20, 4, 18, 381828, tzinfo=utc), null=True, verbose_name='Fecha de inicio', blank=True)),
                ('estrategia', models.IntegerField(default=2, verbose_name='Estrategia de planificaci\xf3n', choices=[(2, 'PLM (Modelo Tiempo Cont\xednuo) + Heur\xedstica basada en dependencias')])),
                ('tiempo_minimo_intervalo', models.DecimalField(default=60, help_text='Tiempo m\xednimo de cada intervalo que compone el cronograma. NO ser\xe1 tenido en cuenta durante la resoluci\xf3n del modelo lineal. Esto quiere decir que si la resoluci\xf3n del modelo lineal obtiene intervalos con tiempo menor al definido, estos ser\xe1n incorporados al cronograma.', verbose_name='Tiempo m\xednimo de cada intervalo (min)', max_digits=8, decimal_places=2)),
                ('optimizar_planificacion', models.BooleanField(default=True, help_text='Una vez obtenida la planificaci\xf3n intenta optimizarla un poco m\xe1s.', verbose_name='Optimizar planificaci\xf3n')),
                ('estado', models.IntegerField(default=0, verbose_name='Estado', editable=False, choices=[(0, 'Inv\xe1lido'), (1, 'V\xe1lido'), (2, 'Activo'), (3, 'Finalizado'), (4, 'Cancelado')])),
                ('tolerancia', models.DecimalField(default=0.005, help_text='Tolerancia a errores de planificaci\xf3n. Indica el factor de tolerancia a los errores durante la planificaci\xf3n. Por ejemplo, un valor de 0.02 para un item de un pedido con cantidad 100, indica que puede haber un error de planificaci\xf3n de 2 unidades.', verbose_name='Tolerancia a errores de planificaci\xf3n.', max_digits=3, decimal_places=3)),
                ('_particionar_pedidos', models.BooleanField(default=True, help_text='Seleccionando esta opci\xf3n se estimar\xe1 cuanto demora la fabricaci\xf3n de cada producto. Luego en funci\xf3n de la estimaci\xf3n se calcular\xe1 el ideal de la cantidad de productos por item para aproximarse al tiempo de producci\xf3n por item indicado.', verbose_name='Particionar pedidos')),
                ('tiempo_produccion_por_item', models.DecimalField(default=40, help_text='Indica el tiempo de producci\xf3n esperado por item en horas. Sirve para subdividir en forma automatica en varios items los productos de un pedido de forma de poder organizar mejor los lotes de producci\xf3n y reducir notablemente los tiempos de planificaci\xf3n', verbose_name='Tiempo de producci\xf3n por item (horas)', max_digits=8, decimal_places=2)),
                ('cantidad_extra_tarea_anterior', models.DecimalField(default=0, help_text='Sean A y B dos tareas, donde A depende de B (B debe producirse antes que A). Este par\xe1metro indica, si queremos planificar B, a partir de que instante puede planificarse en funci\xf3n de la cantidad que ya est\xe1 producida de A. Por ejemplo, si esta cantidad es 2 y se quiere producir 50 de A y 50 de B, si hasta el instanet t1 tenemos planificado A(12) y B(10), y en hasta el instante t2 tenemos planificado A(20) y B(10), entonces entre t1 y t2, podremos planificar una cantidad de 8 para B.', verbose_name='Cantidad Extra en Tarea Anterior', max_digits=8, decimal_places=2)),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'Cronograma',
                'verbose_name_plural': 'Cronogramas',
            },
        ),
        migrations.CreateModel(
            name='IntervaloCronograma',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cantidad_tarea', models.DecimalField(decimal_places=6, default=0, editable=False, max_digits=12, help_text='Cantidad de tarea a producir en el intervalo.', verbose_name='Cantidad Tarea Planificada')),
                ('cantidad_tarea_real', models.DecimalField(default=0, help_text='Cantidad de tarea producida (real).', verbose_name='Cantidad Tarea Real', max_digits=8, decimal_places=2)),
                ('tiempo_intervalo', models.DecimalField(verbose_name='Tiempo del intervalo (min)', max_digits=12, decimal_places=6)),
                ('fecha_desde', models.DateTimeField(verbose_name='Fecha desde')),
                ('fecha_hasta', models.DateTimeField(null=True, verbose_name='Fecha hasta')),
                ('estado', models.IntegerField(default=0, verbose_name='Estado', editable=False, choices=[(0, 'Planificado'), (1, 'Activo'), (2, 'Finalizado'), (3, 'Cancelado')])),
                ('cronograma', models.ForeignKey(verbose_name='Cronograma', to='planificacion.Cronograma')),
            ],
            options={
                'ordering': ['-cronograma__id', 'fecha_desde'],
                'verbose_name': 'Intervalo cronograma',
                'verbose_name_plural': 'Intervalos cronograma',
            },
        ),
        migrations.CreateModel(
            name='MaquinaCronograma',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cronograma', models.ForeignKey(verbose_name='Cronograma', to='planificacion.Cronograma')),
            ],
            options={
                'ordering': ['maquina__descripcion'],
                'verbose_name': 'Maquina cronograma',
                'verbose_name_plural': 'Maquina cronograma',
            },
        ),
        migrations.CreateModel(
            name='PedidoCronograma',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cronograma', models.ForeignKey(verbose_name='Cronograma', to='planificacion.Cronograma')),
            ],
            options={
                'ordering': ['pedido__descripcion'],
                'verbose_name': 'Pedido cronograma',
                'verbose_name_plural': 'Pedidos cronograma',
            },
        ),
        migrations.CreateModel(
            name='TareaItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cantidad_realizada', models.DecimalField(default=0, help_text='Cantidad de tarea realizada (real).', verbose_name='Cantidad Realizada', max_digits=8, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ItemPlanificable',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('produccion.itempedido',),
        ),
        migrations.CreateModel(
            name='MaquinaPlanificacion',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('produccion.maquina',),
        ),
        migrations.CreateModel(
            name='PedidoPlanificable',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('produccion.pedido',),
        ),
        migrations.AddField(
            model_name='tareaitem',
            name='item',
            field=models.ForeignKey(verbose_name='Item', to='planificacion.ItemPlanificable'),
        ),
        migrations.AddField(
            model_name='tareaitem',
            name='tarea',
            field=models.ForeignKey(verbose_name='Tarea', to='produccion.Tarea'),
        ),
        migrations.AddField(
            model_name='pedidocronograma',
            name='pedido',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Pedido', to='planificacion.PedidoPlanificable'),
        ),
        migrations.AddField(
            model_name='maquinacronograma',
            name='maquina',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='M\xe1quina', to='planificacion.MaquinaPlanificacion'),
        ),
        migrations.AddField(
            model_name='intervalocronograma',
            name='item',
            field=models.ForeignKey(editable=False, to='planificacion.ItemPlanificable', null=True),
        ),
        migrations.AddField(
            model_name='intervalocronograma',
            name='maquina',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='M\xe1quina', to='planificacion.MaquinaPlanificacion'),
        ),
        migrations.AddField(
            model_name='intervalocronograma',
            name='maquinacronograma',
            field=models.ForeignKey(editable=False, to='planificacion.MaquinaCronograma'),
        ),
        migrations.AddField(
            model_name='intervalocronograma',
            name='pedido',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, editable=False, to='planificacion.PedidoPlanificable', verbose_name='Pedido'),
        ),
        migrations.AddField(
            model_name='intervalocronograma',
            name='pedidocronograma',
            field=models.ForeignKey(editable=False, to='planificacion.PedidoCronograma'),
        ),
        migrations.AddField(
            model_name='intervalocronograma',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, editable=False, to='produccion.Producto', verbose_name='Producto'),
        ),
        migrations.AddField(
            model_name='intervalocronograma',
            name='tarea',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Tarea', to='produccion.Tarea'),
        ),
        migrations.AddField(
            model_name='intervalocronograma',
            name='tareamaquina',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, editable=False, to='produccion.TareaMaquina'),
        ),
        migrations.AddField(
            model_name='intervalocronograma',
            name='tareaproducto',
            field=models.ForeignKey(editable=False, to='produccion.TareaProducto'),
        ),
        migrations.AlterUniqueTogether(
            name='pedidocronograma',
            unique_together=set([('cronograma', 'pedido')]),
        ),
        migrations.AlterUniqueTogether(
            name='maquinacronograma',
            unique_together=set([('cronograma', 'maquina')]),
        ),
        migrations.AlterUniqueTogether(
            name='intervalocronograma',
            unique_together=set([('cronograma', 'maquina', 'fecha_desde')]),
        ),
    ]

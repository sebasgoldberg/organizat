# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DependenciaTareaProducto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'ordering': ['producto__descripcion', 'tarea__descripcion', 'tarea_anterior__descripcion'],
                'verbose_name': 'Dependencia de tareas en producto',
                'verbose_name_plural': 'Dependencias de tareas en productos',
            },
        ),
        migrations.CreateModel(
            name='ItemPedido',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cantidad', models.DecimalField(verbose_name='Cantidad', max_digits=7, decimal_places=2)),
            ],
            options={
                'ordering': ['-pedido__id', 'producto__descripcion'],
                'verbose_name': 'Item pedido',
                'verbose_name_plural': 'Items pedidos',
            },
        ),
        migrations.CreateModel(
            name='Maquina',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descripcion', models.CharField(unique=True, max_length=100, verbose_name='Descripci\xf3n')),
            ],
            options={
                'ordering': ['descripcion'],
                'verbose_name': 'Maquina',
                'verbose_name_plural': 'Maquinas',
            },
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descripcion', models.CharField(max_length=100, null=True, verbose_name='Descripci\xf3n')),
            ],
            options={
                'ordering': ['-id'],
                'verbose_name': 'Pedido',
                'verbose_name_plural': 'Pedidos',
            },
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descripcion', models.CharField(max_length=100, unique=True, null=True, verbose_name='Descripci\xf3n')),
            ],
            options={
                'ordering': ['descripcion'],
                'verbose_name': 'Producto',
                'verbose_name_plural': 'Productos',
            },
        ),
        migrations.CreateModel(
            name='Tarea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('descripcion', models.CharField(unique=True, max_length=100, verbose_name='Descripci\xf3n')),
                ('tiempo', models.DecimalField(help_text='Tiempo necesario para realizar la tarea por unidad de producto.', verbose_name='Tiempo (min)', max_digits=7, decimal_places=2)),
            ],
            options={
                'ordering': ['descripcion'],
                'verbose_name': 'Tarea',
                'verbose_name_plural': 'Tareas',
            },
        ),
        migrations.CreateModel(
            name='TareaMaquina',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('maquina', models.ForeignKey(verbose_name='Maquina', to='produccion.Maquina')),
                ('tarea', models.ForeignKey(verbose_name='Tarea', to='produccion.Tarea')),
            ],
            options={
                'ordering': ['maquina__descripcion', 'tarea__descripcion'],
                'verbose_name': 'Tarea de una m\xe1quina',
                'verbose_name_plural': 'Tareas por m\xe1quinas',
            },
        ),
        migrations.CreateModel(
            name='TareaProducto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('producto', models.ForeignKey(verbose_name='Producto', to='produccion.Producto')),
                ('tarea', models.ForeignKey(verbose_name='Tarea', to='produccion.Tarea')),
            ],
            options={
                'ordering': ['producto__descripcion', 'tarea__descripcion'],
                'verbose_name': 'Tarea a realizar en producto',
                'verbose_name_plural': 'Tareas por productos',
            },
        ),
        migrations.CreateModel(
            name='TiempoRealizacionTarea',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tiempo', models.DecimalField(help_text='Tiempo para realizar la tarea en la m\xe1quina y producto indicados, por unidad de producto.', verbose_name='Tiempo (min)', max_digits=7, decimal_places=2)),
                ('activa', models.BooleanField(default=True, help_text='Indica si la tarea se puede realizar en la m\xe1quina para el producto dado.', verbose_name='Activa')),
                ('maquina', models.ForeignKey(editable=False, to='produccion.Maquina', verbose_name='Maquina')),
                ('producto', models.ForeignKey(editable=False, to='produccion.Producto', verbose_name='Producto')),
                ('tarea', models.ForeignKey(editable=False, to='produccion.Tarea', verbose_name='Tarea')),
                ('tareamaquina', models.ForeignKey(editable=False, to='produccion.TareaMaquina')),
                ('tareaproducto', models.ForeignKey(editable=False, to='produccion.TareaProducto')),
            ],
            options={
                'ordering': ['maquina__descripcion', 'producto__descripcion', 'tarea__descripcion'],
                'verbose_name': 'Tiempo de producci\xf3n',
                'verbose_name_plural': 'Tiempos de producci\xf3n',
            },
        ),
        migrations.AddField(
            model_name='itempedido',
            name='pedido',
            field=models.ForeignKey(verbose_name='Pedido', to='produccion.Pedido'),
        ),
        migrations.AddField(
            model_name='itempedido',
            name='producto',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, verbose_name='Producto', to='produccion.Producto'),
        ),
        migrations.AddField(
            model_name='dependenciatareaproducto',
            name='producto',
            field=models.ForeignKey(verbose_name='Tarea en m\xe1quina', to='produccion.Producto'),
        ),
        migrations.AddField(
            model_name='dependenciatareaproducto',
            name='tarea',
            field=models.ForeignKey(related_name='mis_dependencias', verbose_name='La tarea', to='produccion.Tarea'),
        ),
        migrations.AddField(
            model_name='dependenciatareaproducto',
            name='tarea_anterior',
            field=models.ForeignKey(related_name='dependientes_de_mi', verbose_name='Depende de la tarea', to='produccion.Tarea', help_text='Esta tarea debe realizarse antes'),
        ),
        migrations.AddField(
            model_name='dependenciatareaproducto',
            name='tarea_anteriorproducto',
            field=models.ForeignKey(related_name='dependientes_de_mi', editable=False, to='produccion.TareaProducto'),
        ),
        migrations.AddField(
            model_name='dependenciatareaproducto',
            name='tareaproducto',
            field=models.ForeignKey(related_name='mis_dependencias', editable=False, to='produccion.TareaProducto'),
        ),
        migrations.CreateModel(
            name='ProductoProxyDependenciasTareas',
            fields=[
            ],
            options={
                'ordering': ['descripcion'],
                'verbose_name': 'Dependencia de tarea en producto',
                'proxy': True,
                'verbose_name_plural': 'Dependencias de tareas en productos',
            },
            bases=('produccion.producto',),
        ),
        migrations.AlterUniqueTogether(
            name='tiemporealizaciontarea',
            unique_together=set([('maquina', 'producto', 'tarea')]),
        ),
        migrations.AlterUniqueTogether(
            name='tareaproducto',
            unique_together=set([('producto', 'tarea')]),
        ),
        migrations.AlterUniqueTogether(
            name='tareamaquina',
            unique_together=set([('maquina', 'tarea')]),
        ),
        migrations.AlterUniqueTogether(
            name='dependenciatareaproducto',
            unique_together=set([('producto', 'tarea', 'tarea_anterior')]),
        ),
    ]

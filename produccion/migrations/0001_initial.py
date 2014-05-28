# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Maquina'
        db.create_table(u'produccion_maquina', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('descripcion', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal(u'produccion', ['Maquina'])

        # Adding model 'Tarea'
        db.create_table(u'produccion_tarea', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('descripcion', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('tiempo', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2)),
        ))
        db.send_create_signal(u'produccion', ['Tarea'])

        # Adding model 'TareaMaquina'
        db.create_table(u'produccion_tareamaquina', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('maquina', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['produccion.Maquina'])),
            ('tarea', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['produccion.Tarea'])),
        ))
        db.send_create_signal(u'produccion', ['TareaMaquina'])

        # Adding unique constraint on 'TareaMaquina', fields ['maquina', 'tarea']
        db.create_unique(u'produccion_tareamaquina', ['maquina_id', 'tarea_id'])

        # Adding model 'Producto'
        db.create_table(u'produccion_producto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('descripcion', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
        ))
        db.send_create_signal(u'produccion', ['Producto'])

        # Adding model 'TareaProducto'
        db.create_table(u'produccion_tareaproducto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('producto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['produccion.Producto'])),
            ('tarea', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['produccion.Tarea'])),
        ))
        db.send_create_signal(u'produccion', ['TareaProducto'])

        # Adding unique constraint on 'TareaProducto', fields ['producto', 'tarea']
        db.create_unique(u'produccion_tareaproducto', ['producto_id', 'tarea_id'])

        # Adding model 'TiempoRealizacionTarea'
        db.create_table(u'produccion_tiemporealizaciontarea', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('maquina', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['produccion.Maquina'])),
            ('producto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['produccion.Producto'])),
            ('tarea', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['produccion.Tarea'])),
            ('tiempo', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2)),
            ('activa', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('tareamaquina', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['produccion.TareaMaquina'])),
            ('tareaproducto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['produccion.TareaProducto'])),
        ))
        db.send_create_signal(u'produccion', ['TiempoRealizacionTarea'])

        # Adding unique constraint on 'TiempoRealizacionTarea', fields ['maquina', 'producto', 'tarea']
        db.create_unique(u'produccion_tiemporealizaciontarea', ['maquina_id', 'producto_id', 'tarea_id'])

        # Adding model 'DependenciaTareaProducto'
        db.create_table(u'produccion_dependenciatareaproducto', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('producto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['produccion.Producto'])),
            ('tarea', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mis_dependencias', to=orm['produccion.Tarea'])),
            ('tarea_anterior', self.gf('django.db.models.fields.related.ForeignKey')(related_name='dependientes_de_mi', to=orm['produccion.Tarea'])),
            ('tareaproducto', self.gf('django.db.models.fields.related.ForeignKey')(related_name='mis_dependencias', to=orm['produccion.TareaProducto'])),
            ('tarea_anteriorproducto', self.gf('django.db.models.fields.related.ForeignKey')(related_name='dependientes_de_mi', to=orm['produccion.TareaProducto'])),
        ))
        db.send_create_signal(u'produccion', ['DependenciaTareaProducto'])

        # Adding unique constraint on 'DependenciaTareaProducto', fields ['producto', 'tarea', 'tarea_anterior']
        db.create_unique(u'produccion_dependenciatareaproducto', ['producto_id', 'tarea_id', 'tarea_anterior_id'])

        # Adding model 'Pedido'
        db.create_table(u'produccion_pedido', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('descripcion', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'produccion', ['Pedido'])

        # Adding model 'ItemPedido'
        db.create_table(u'produccion_itempedido', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pedido', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['produccion.Pedido'])),
            ('producto', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['produccion.Producto'], on_delete=models.PROTECT)),
            ('cantidad', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2)),
        ))
        db.send_create_signal(u'produccion', ['ItemPedido'])

        # Adding unique constraint on 'ItemPedido', fields ['pedido', 'producto']
        db.create_unique(u'produccion_itempedido', ['pedido_id', 'producto_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ItemPedido', fields ['pedido', 'producto']
        db.delete_unique(u'produccion_itempedido', ['pedido_id', 'producto_id'])

        # Removing unique constraint on 'DependenciaTareaProducto', fields ['producto', 'tarea', 'tarea_anterior']
        db.delete_unique(u'produccion_dependenciatareaproducto', ['producto_id', 'tarea_id', 'tarea_anterior_id'])

        # Removing unique constraint on 'TiempoRealizacionTarea', fields ['maquina', 'producto', 'tarea']
        db.delete_unique(u'produccion_tiemporealizaciontarea', ['maquina_id', 'producto_id', 'tarea_id'])

        # Removing unique constraint on 'TareaProducto', fields ['producto', 'tarea']
        db.delete_unique(u'produccion_tareaproducto', ['producto_id', 'tarea_id'])

        # Removing unique constraint on 'TareaMaquina', fields ['maquina', 'tarea']
        db.delete_unique(u'produccion_tareamaquina', ['maquina_id', 'tarea_id'])

        # Deleting model 'Maquina'
        db.delete_table(u'produccion_maquina')

        # Deleting model 'Tarea'
        db.delete_table(u'produccion_tarea')

        # Deleting model 'TareaMaquina'
        db.delete_table(u'produccion_tareamaquina')

        # Deleting model 'Producto'
        db.delete_table(u'produccion_producto')

        # Deleting model 'TareaProducto'
        db.delete_table(u'produccion_tareaproducto')

        # Deleting model 'TiempoRealizacionTarea'
        db.delete_table(u'produccion_tiemporealizaciontarea')

        # Deleting model 'DependenciaTareaProducto'
        db.delete_table(u'produccion_dependenciatareaproducto')

        # Deleting model 'Pedido'
        db.delete_table(u'produccion_pedido')

        # Deleting model 'ItemPedido'
        db.delete_table(u'produccion_itempedido')


    models = {
        u'produccion.dependenciatareaproducto': {
            'Meta': {'ordering': "['producto__descripcion', 'tarea__descripcion', 'tarea_anterior__descripcion']", 'unique_together': "(('producto', 'tarea', 'tarea_anterior'),)", 'object_name': 'DependenciaTareaProducto'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'producto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Producto']"}),
            'tarea': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mis_dependencias'", 'to': u"orm['produccion.Tarea']"}),
            'tarea_anterior': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dependientes_de_mi'", 'to': u"orm['produccion.Tarea']"}),
            'tarea_anteriorproducto': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'dependientes_de_mi'", 'to': u"orm['produccion.TareaProducto']"}),
            'tareaproducto': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'mis_dependencias'", 'to': u"orm['produccion.TareaProducto']"})
        },
        u'produccion.itempedido': {
            'Meta': {'ordering': "['-pedido__id', 'producto__descripcion']", 'unique_together': "(('pedido', 'producto'),)", 'object_name': 'ItemPedido'},
            'cantidad': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pedido': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Pedido']"}),
            'producto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Producto']", 'on_delete': 'models.PROTECT'})
        },
        u'produccion.maquina': {
            'Meta': {'ordering': "['descripcion']", 'object_name': 'Maquina'},
            'descripcion': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'produccion.pedido': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Pedido'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'produccion.producto': {
            'Meta': {'ordering': "['descripcion']", 'object_name': 'Producto'},
            'descripcion': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'produccion.tarea': {
            'Meta': {'ordering': "['descripcion']", 'object_name': 'Tarea'},
            'descripcion': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tiempo': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'})
        },
        u'produccion.tareamaquina': {
            'Meta': {'ordering': "['maquina__descripcion', 'tarea__descripcion']", 'unique_together': "(('maquina', 'tarea'),)", 'object_name': 'TareaMaquina'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maquina': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Maquina']"}),
            'tarea': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Tarea']"})
        },
        u'produccion.tareaproducto': {
            'Meta': {'ordering': "['producto__descripcion', 'tarea__descripcion']", 'unique_together': "(('producto', 'tarea'),)", 'object_name': 'TareaProducto'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'producto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Producto']"}),
            'tarea': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Tarea']"})
        },
        u'produccion.tiemporealizaciontarea': {
            'Meta': {'ordering': "['maquina__descripcion', 'producto__descripcion', 'tarea__descripcion']", 'unique_together': "(('maquina', 'producto', 'tarea'),)", 'object_name': 'TiempoRealizacionTarea'},
            'activa': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maquina': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Maquina']"}),
            'producto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Producto']"}),
            'tarea': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Tarea']"}),
            'tareamaquina': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.TareaMaquina']"}),
            'tareaproducto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.TareaProducto']"}),
            'tiempo': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'})
        }
    }

    complete_apps = ['produccion']
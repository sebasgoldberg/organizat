# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Producto.descripcion'
        db.alter_column(u'produccion_producto', 'descripcion', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True, null=True))

        # Changing field 'Pedido.descripcion'
        db.alter_column(u'produccion_pedido', 'descripcion', self.gf('django.db.models.fields.CharField')(max_length=100, null=True))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Producto.descripcion'
        raise RuntimeError("Cannot reverse this migration. 'Producto.descripcion' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Producto.descripcion'
        db.alter_column(u'produccion_producto', 'descripcion', self.gf('django.db.models.fields.CharField')(max_length=100, unique=True))

        # User chose to not deal with backwards NULL issues for 'Pedido.descripcion'
        raise RuntimeError("Cannot reverse this migration. 'Pedido.descripcion' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration
        # Changing field 'Pedido.descripcion'
        db.alter_column(u'produccion_pedido', 'descripcion', self.gf('django.db.models.fields.CharField')(max_length=100))

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
            'Meta': {'ordering': "['-pedido__id', 'producto__descripcion']", 'object_name': 'ItemPedido'},
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
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'produccion.producto': {
            'Meta': {'ordering': "['descripcion']", 'object_name': 'Producto'},
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True', 'null': 'True'}),
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
# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'IntervaloCronograma', fields ['cronograma', 'maquina', 'secuencia']
        db.delete_unique(u'planificacion_intervalocronograma', ['cronograma_id', 'maquina_id', 'secuencia'])

        # Deleting field 'IntervaloCronograma.cantidad_producto'
        db.delete_column(u'planificacion_intervalocronograma', 'cantidad_producto')

        # Deleting field 'IntervaloCronograma.secuencia'
        db.delete_column(u'planificacion_intervalocronograma', 'secuencia')

        # Adding field 'IntervaloCronograma.cantidad_tarea_real'
        db.add_column(u'planificacion_intervalocronograma', 'cantidad_tarea_real',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=7, decimal_places=2),
                      keep_default=False)

        # Adding unique constraint on 'IntervaloCronograma', fields ['cronograma', 'maquina', 'fecha_desde']
        db.create_unique(u'planificacion_intervalocronograma', ['cronograma_id', 'maquina_id', 'fecha_desde'])


    def backwards(self, orm):
        # Removing unique constraint on 'IntervaloCronograma', fields ['cronograma', 'maquina', 'fecha_desde']
        db.delete_unique(u'planificacion_intervalocronograma', ['cronograma_id', 'maquina_id', 'fecha_desde'])

        # Adding field 'IntervaloCronograma.cantidad_producto'
        db.add_column(u'planificacion_intervalocronograma', 'cantidad_producto',
                      self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=7, decimal_places=2),
                      keep_default=False)

        # Adding field 'IntervaloCronograma.secuencia'
        db.add_column(u'planificacion_intervalocronograma', 'secuencia',
                      self.gf('django.db.models.fields.IntegerField')(null=True, blank=True),
                      keep_default=False)

        # Deleting field 'IntervaloCronograma.cantidad_tarea_real'
        db.delete_column(u'planificacion_intervalocronograma', 'cantidad_tarea_real')

        # Adding unique constraint on 'IntervaloCronograma', fields ['cronograma', 'maquina', 'secuencia']
        db.create_unique(u'planificacion_intervalocronograma', ['cronograma_id', 'maquina_id', 'secuencia'])


    models = {
        u'planificacion.cronograma': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Cronograma'},
            'descripcion': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'estado': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'estrategia': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'fecha_inicio': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 5, 24, 0, 0)', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'optimizar_planificacion': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tiempo_minimo_intervalo': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'})
        },
        u'planificacion.intervalocronograma': {
            'Meta': {'ordering': "['-cronograma__id', 'fecha_desde']", 'unique_together': "(('cronograma', 'maquina', 'fecha_desde'),)", 'object_name': 'IntervaloCronograma'},
            'cantidad_tarea': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'cantidad_tarea_real': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'cronograma': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planificacion.Cronograma']"}),
            'fecha_desde': ('django.db.models.fields.DateTimeField', [], {}),
            'fecha_hasta': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'itempedido': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.ItemPedido']", 'on_delete': 'models.PROTECT'}),
            'maquina': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Maquina']", 'on_delete': 'models.PROTECT'}),
            'maquinacronograma': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planificacion.MaquinaCronograma']"}),
            'pedido': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Pedido']", 'on_delete': 'models.PROTECT'}),
            'pedidocronograma': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planificacion.PedidoCronograma']"}),
            'producto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Producto']", 'on_delete': 'models.PROTECT'}),
            'tarea': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Tarea']", 'on_delete': 'models.PROTECT'}),
            'tareamaquina': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.TareaMaquina']", 'on_delete': 'models.PROTECT'}),
            'tareaproducto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.TareaProducto']", 'on_delete': 'models.PROTECT'}),
            'tiempo_intervalo': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'})
        },
        u'planificacion.maquinacronograma': {
            'Meta': {'ordering': "['maquina__descripcion']", 'unique_together': "(('cronograma', 'maquina'),)", 'object_name': 'MaquinaCronograma'},
            'cronograma': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planificacion.Cronograma']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maquina': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Maquina']", 'on_delete': 'models.PROTECT'})
        },
        u'planificacion.pedidocronograma': {
            'Meta': {'ordering': "['pedido__descripcion']", 'unique_together': "(('cronograma', 'pedido'),)", 'object_name': 'PedidoCronograma'},
            'cronograma': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planificacion.Cronograma']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'pedido': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Pedido']", 'on_delete': 'models.PROTECT'})
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
        }
    }

    complete_apps = ['planificacion']
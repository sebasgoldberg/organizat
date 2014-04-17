# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Cronograma.tiempo_minimo_intervalo'
        db.add_column(u'planificacion_cronograma', 'tiempo_minimo_intervalo',
                      self.gf('django.db.models.fields.DecimalField')(default=120, max_digits=7, decimal_places=2),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Cronograma.tiempo_minimo_intervalo'
        db.delete_column(u'planificacion_cronograma', 'tiempo_minimo_intervalo')


    models = {
        u'planificacion.cronograma': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Cronograma'},
            'descripcion': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'estrategia': ('django.db.models.fields.IntegerField', [], {}),
            'fecha_inicio': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 4, 17, 0, 0)', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intervalo_tiempo': ('django.db.models.fields.DecimalField', [], {'max_digits': '7', 'decimal_places': '2'}),
            'tiempo_minimo_intervalo': ('django.db.models.fields.DecimalField', [], {'default': '120', 'max_digits': '7', 'decimal_places': '2'})
        },
        u'planificacion.intervalocronograma': {
            'Meta': {'ordering': "['-cronograma__id', 'maquina__descripcion', 'secuencia']", 'unique_together': "(('cronograma', 'maquina', 'secuencia'),)", 'object_name': 'IntervaloCronograma'},
            'cantidad_producto': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'cantidad_tarea': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '7', 'decimal_places': '2'}),
            'cronograma': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planificacion.Cronograma']"}),
            'fecha_desde': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'itempedido': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.ItemPedido']", 'on_delete': 'models.PROTECT'}),
            'maquina': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Maquina']", 'on_delete': 'models.PROTECT'}),
            'maquinacronograma': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planificacion.MaquinaCronograma']"}),
            'pedido': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Pedido']", 'on_delete': 'models.PROTECT'}),
            'pedidocronograma': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planificacion.PedidoCronograma']"}),
            'producto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Producto']", 'on_delete': 'models.PROTECT'}),
            'secuencia': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'tarea': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Tarea']", 'on_delete': 'models.PROTECT'}),
            'tareamaquina': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.TareaMaquina']", 'on_delete': 'models.PROTECT'}),
            'tareaproducto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.TareaProducto']", 'on_delete': 'models.PROTECT'}),
            'tiempo_intervalo': ('django.db.models.fields.IntegerField', [], {})
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
            'fecha_entrega': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
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
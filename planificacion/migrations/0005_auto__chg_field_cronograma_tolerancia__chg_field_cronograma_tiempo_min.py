# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Cronograma.tolerancia'
        db.alter_column(u'planificacion_cronograma', 'tolerancia', self.gf('django.db.models.fields.DecimalField')(max_digits=3, decimal_places=3))

        # Changing field 'Cronograma.tiempo_minimo_intervalo'
        db.alter_column(u'planificacion_cronograma', 'tiempo_minimo_intervalo', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2))

        # Changing field 'IntervaloCronograma.cantidad_tarea'
        db.alter_column(u'planificacion_intervalocronograma', 'cantidad_tarea', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=6))

        # Changing field 'IntervaloCronograma.cantidad_tarea_real'
        db.alter_column(u'planificacion_intervalocronograma', 'cantidad_tarea_real', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2))

        # Changing field 'IntervaloCronograma.tiempo_intervalo'
        db.alter_column(u'planificacion_intervalocronograma', 'tiempo_intervalo', self.gf('django.db.models.fields.DecimalField')(max_digits=12, decimal_places=6))

        # Changing field 'TareaItem.cantidad_realizada'
        db.alter_column(u'planificacion_tareaitem', 'cantidad_realizada', self.gf('django.db.models.fields.DecimalField')(max_digits=8, decimal_places=2))

    def backwards(self, orm):

        # Changing field 'Cronograma.tolerancia'
        db.alter_column(u'planificacion_cronograma', 'tolerancia', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2))

        # Changing field 'Cronograma.tiempo_minimo_intervalo'
        db.alter_column(u'planificacion_cronograma', 'tiempo_minimo_intervalo', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2))

        # Changing field 'IntervaloCronograma.cantidad_tarea'
        db.alter_column(u'planificacion_intervalocronograma', 'cantidad_tarea', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2))

        # Changing field 'IntervaloCronograma.cantidad_tarea_real'
        db.alter_column(u'planificacion_intervalocronograma', 'cantidad_tarea_real', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2))

        # Changing field 'IntervaloCronograma.tiempo_intervalo'
        db.alter_column(u'planificacion_intervalocronograma', 'tiempo_intervalo', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2))

        # Changing field 'TareaItem.cantidad_realizada'
        db.alter_column(u'planificacion_tareaitem', 'cantidad_realizada', self.gf('django.db.models.fields.DecimalField')(max_digits=7, decimal_places=2))

    models = {
        u'planificacion.cronograma': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Cronograma'},
            'descripcion': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'estado': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'estrategia': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'fecha_inicio': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 9, 5, 0, 0)', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'optimizar_planificacion': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tiempo_minimo_intervalo': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '8', 'decimal_places': '2'}),
            'tolerancia': ('django.db.models.fields.DecimalField', [], {'default': '0.001', 'max_digits': '3', 'decimal_places': '3'})
        },
        u'planificacion.intervalocronograma': {
            'Meta': {'ordering': "['-cronograma__id', 'fecha_desde']", 'unique_together': "(('cronograma', 'maquina', 'fecha_desde'),)", 'object_name': 'IntervaloCronograma'},
            'cantidad_tarea': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '6'}),
            'cantidad_tarea_real': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '8', 'decimal_places': '2'}),
            'cronograma': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planificacion.Cronograma']"}),
            'estado': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'fecha_desde': ('django.db.models.fields.DateTimeField', [], {}),
            'fecha_hasta': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.ItemPedido']", 'null': 'True', 'on_delete': 'models.PROTECT'}),
            'maquina': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Maquina']", 'on_delete': 'models.PROTECT'}),
            'maquinacronograma': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planificacion.MaquinaCronograma']"}),
            'pedido': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Pedido']", 'on_delete': 'models.PROTECT'}),
            'pedidocronograma': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planificacion.PedidoCronograma']"}),
            'producto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Producto']", 'on_delete': 'models.PROTECT'}),
            'tarea': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Tarea']", 'on_delete': 'models.PROTECT'}),
            'tareamaquina': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.TareaMaquina']", 'on_delete': 'models.PROTECT'}),
            'tareaproducto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.TareaProducto']", 'on_delete': 'models.PROTECT'}),
            'tiempo_intervalo': ('django.db.models.fields.DecimalField', [], {'max_digits': '12', 'decimal_places': '6'})
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
        u'planificacion.tareaitem': {
            'Meta': {'object_name': 'TareaItem'},
            'cantidad_realizada': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '8', 'decimal_places': '2'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.ItemPedido']"}),
            'tarea': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Tarea']"})
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
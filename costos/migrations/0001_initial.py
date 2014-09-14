# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'CostoMaquina'
        db.create_table(u'costos_costomaquina', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('maquina', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['produccion.Maquina'])),
            ('costo_por_hora', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=12, decimal_places=3)),
        ))
        db.send_create_signal(u'costos', ['CostoMaquina'])

        # Adding model 'CostoIntervalo'
        db.create_table(u'costos_costointervalo', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('costo', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=12, decimal_places=3)),
            ('intervalo', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['planificacion.IntervaloCronograma'], unique=True)),
        ))
        db.send_create_signal(u'costos', ['CostoIntervalo'])


    def backwards(self, orm):
        # Deleting model 'CostoMaquina'
        db.delete_table(u'costos_costomaquina')

        # Deleting model 'CostoIntervalo'
        db.delete_table(u'costos_costointervalo')


    models = {
        u'costos.costointervalo': {
            'Meta': {'object_name': 'CostoIntervalo'},
            'costo': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'intervalo': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planificacion.IntervaloCronograma']", 'unique': 'True'})
        },
        u'costos.costomaquina': {
            'Meta': {'object_name': 'CostoMaquina'},
            'costo_por_hora': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '12', 'decimal_places': '3'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'maquina': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Maquina']"})
        },
        u'planificacion.cronograma': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Cronograma'},
            '_particionar_pedidos': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'cantidad_extra_tarea_anterior': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '8', 'decimal_places': '2'}),
            'descripcion': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'estado': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'estrategia': ('django.db.models.fields.IntegerField', [], {'default': '2'}),
            'fecha_inicio': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2014, 9, 14, 0, 0)', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'optimizar_planificacion': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'tiempo_minimo_intervalo': ('django.db.models.fields.DecimalField', [], {'default': '60', 'max_digits': '8', 'decimal_places': '2'}),
            'tiempo_produccion_por_item': ('django.db.models.fields.DecimalField', [], {'default': '40', 'max_digits': '8', 'decimal_places': '2'}),
            'tolerancia': ('django.db.models.fields.DecimalField', [], {'default': '0.005', 'max_digits': '3', 'decimal_places': '3'})
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
            'item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.ItemPedido']", 'null': 'True'}),
            'maquina': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Maquina']", 'on_delete': 'models.PROTECT'}),
            'maquinacronograma': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planificacion.MaquinaCronograma']"}),
            'pedido': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Pedido']", 'on_delete': 'models.PROTECT'}),
            'pedidocronograma': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['planificacion.PedidoCronograma']"}),
            'producto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Producto']", 'on_delete': 'models.PROTECT'}),
            'tarea': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.Tarea']", 'on_delete': 'models.PROTECT'}),
            'tareamaquina': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.TareaMaquina']", 'on_delete': 'models.PROTECT'}),
            'tareaproducto': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['produccion.TareaProducto']"}),
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
        }
    }

    complete_apps = ['costos']
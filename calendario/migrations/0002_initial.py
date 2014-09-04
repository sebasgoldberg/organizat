# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Calendario'
        db.create_table(u'calendario_calendario', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal(u'calendario', ['Calendario'])

        # Adding model 'IntervaloLaborable'
        db.create_table(u'calendario_intervalolaborable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('calendario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['calendario.Calendario'])),
            ('dia', self.gf('django.db.models.fields.IntegerField')()),
            ('hora_desde', self.gf('django.db.models.fields.TimeField')()),
            ('hora_hasta', self.gf('django.db.models.fields.TimeField')()),
        ))
        db.send_create_signal(u'calendario', ['IntervaloLaborable'])

        # Adding model 'ExcepcionLaborable'
        db.create_table(u'calendario_excepcionlaborable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('calendario', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['calendario.Calendario'])),
            ('fecha', self.gf('django.db.models.fields.DateField')()),
            ('hora_desde', self.gf('django.db.models.fields.TimeField')()),
            ('hora_hasta', self.gf('django.db.models.fields.TimeField')()),
            ('laborable', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'calendario', ['ExcepcionLaborable'])


    def backwards(self, orm):
        # Deleting model 'Calendario'
        db.delete_table(u'calendario_calendario')

        # Deleting model 'IntervaloLaborable'
        db.delete_table(u'calendario_intervalolaborable')

        # Deleting model 'ExcepcionLaborable'
        db.delete_table(u'calendario_excepcionlaborable')


    models = {
        u'calendario.calendario': {
            'Meta': {'object_name': 'Calendario'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'calendario.excepcionlaborable': {
            'Meta': {'object_name': 'ExcepcionLaborable'},
            'calendario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['calendario.Calendario']"}),
            'fecha': ('django.db.models.fields.DateField', [], {}),
            'hora_desde': ('django.db.models.fields.TimeField', [], {}),
            'hora_hasta': ('django.db.models.fields.TimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'laborable': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'calendario.intervalolaborable': {
            'Meta': {'object_name': 'IntervaloLaborable'},
            'calendario': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['calendario.Calendario']"}),
            'dia': ('django.db.models.fields.IntegerField', [], {}),
            'hora_desde': ('django.db.models.fields.TimeField', [], {}),
            'hora_hasta': ('django.db.models.fields.TimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['calendario']
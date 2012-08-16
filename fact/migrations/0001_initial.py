# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Owner'
        db.create_table('fact_owner', (
            ('user_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True, primary_key=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
        ))
        db.send_create_signal('fact', ['Owner'])

        # Adding model 'Images'
        db.create_table('fact_images', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.files.ImageField')(max_length=100, blank=True)),
        ))
        db.send_create_signal('fact', ['Images'])

        # Adding model 'Organization'
        db.create_table('fact_organization', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('address_extra', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
            ('address_extra2', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('legal_infos', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('owner', self.gf('django.db.models.fields.related.ForeignKey')(related_name='owner', to=orm['fact.Owner'])),
            ('image', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fact.Images'])),
        ))
        db.send_create_signal('fact', ['Organization'])

        # Adding model 'Client'
        db.create_table('fact_client', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('address', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fact.Organization'])),
        ))
        db.send_create_signal('fact', ['Client'])

        # Adding model 'Invoice'
        db.create_table('fact_invoice', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('client', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fact.Client'])),
            ('type', self.gf('django.db.models.fields.CharField')(default='p', max_length=30)),
            ('number', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime(2010, 12, 2, 17, 51, 20, 203449))),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('organization', self.gf('django.db.models.fields.related.ForeignKey')(related_name='invoices', to=orm['fact.Organization'])),
            ('tax', self.gf('django.db.models.fields.BooleanField')(default=False, blank=True)),
            ('tax_rate', self.gf('django.db.models.fields.PositiveIntegerField')(default=18, null=True, blank=True)),
        ))
        db.send_create_signal('fact', ['Invoice'])

        # Adding model 'InvoiceItem'
        db.create_table('fact_invoiceitem', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('invoice', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['fact.Invoice'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('quantity', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('price', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('fact', ['InvoiceItem'])


    def backwards(self, orm):
        
        # Deleting model 'Owner'
        db.delete_table('fact_owner')

        # Deleting model 'Images'
        db.delete_table('fact_images')

        # Deleting model 'Organization'
        db.delete_table('fact_organization')

        # Deleting model 'Client'
        db.delete_table('fact_client')

        # Deleting model 'Invoice'
        db.delete_table('fact_invoice')

        # Deleting model 'InvoiceItem'
        db.delete_table('fact_invoiceitem')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'fact.client': {
            'Meta': {'object_name': 'Client'},
            'address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fact.Organization']"})
        },
        'fact.images': {
            'Meta': {'object_name': 'Images'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'})
        },
        'fact.invoice': {
            'Meta': {'object_name': 'Invoice'},
            'client': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fact.Client']"}),
            'date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime(2010, 12, 2, 17, 51, 20, 216467)'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {}),
            'organization': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'invoices'", 'to': "orm['fact.Organization']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'tax': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'tax_rate': ('django.db.models.fields.PositiveIntegerField', [], {'default': '18', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'p'", 'max_length': '30'})
        },
        'fact.invoiceitem': {
            'Meta': {'object_name': 'InvoiceItem'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoice': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fact.Invoice']", 'null': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'quantity': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'fact.organization': {
            'Meta': {'object_name': 'Organization'},
            'address': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'address_extra': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'address_extra2': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['fact.Images']"}),
            'legal_infos': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'owner'", 'to': "orm['fact.Owner']"})
        },
        'fact.owner': {
            'Meta': {'object_name': 'Owner', '_ormbases': ['auth.User']},
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'user_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True', 'primary_key': 'True'})
        }
    }

    complete_apps = ['fact']

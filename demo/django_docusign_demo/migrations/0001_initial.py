# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SignatureType'
        db.create_table(u'django_docusign_demo_signaturetype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('signature_backend_code', self.gf('django.db.models.fields.CharField')(max_length=50, db_index=True)),
        ))
        db.send_create_signal(u'django_docusign_demo', ['SignatureType'])

        # Adding model 'Signature'
        db.create_table(u'django_docusign_demo_signature', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('signature_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['django_docusign_demo.SignatureType'])),
            ('signature_backend_id', self.gf('django.db.models.fields.CharField')(default=u'', max_length=100, db_index=True, blank=True)),
        ))
        db.send_create_signal(u'django_docusign_demo', ['Signature'])

        # Adding model 'Signer'
        db.create_table(u'django_docusign_demo_signer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('signature', self.gf('django.db.models.fields.related.ForeignKey')(related_name='signers', to=orm['django_docusign_demo.Signature'])),
        ))
        db.send_create_signal(u'django_docusign_demo', ['Signer'])


    def backwards(self, orm):
        # Deleting model 'SignatureType'
        db.delete_table(u'django_docusign_demo_signaturetype')

        # Deleting model 'Signature'
        db.delete_table(u'django_docusign_demo_signature')

        # Deleting model 'Signer'
        db.delete_table(u'django_docusign_demo_signer')


    models = {
        u'django_docusign_demo.signature': {
            'Meta': {'object_name': 'Signature'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signature_backend_id': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '100', 'db_index': 'True', 'blank': 'True'}),
            'signature_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['django_docusign_demo.SignatureType']"})
        },
        u'django_docusign_demo.signaturetype': {
            'Meta': {'object_name': 'SignatureType'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signature_backend_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'})
        },
        u'django_docusign_demo.signer': {
            'Meta': {'object_name': 'Signer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signature': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'signers'", 'to': u"orm['django_docusign_demo.Signature']"})
        }
    }

    complete_apps = ['django_docusign_demo']
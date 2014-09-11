# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Signer.full_name'
        db.add_column(u'django_docusign_demo_signer', 'full_name',
                      self.gf('django.db.models.fields.CharField')(default='John Doe', max_length=50, db_index=True),
                      keep_default=False)

        # Adding field 'Signer.email'
        db.add_column(u'django_docusign_demo_signer', 'email',
                      self.gf('django.db.models.fields.EmailField')(default='john.doe@example.com', max_length=75, db_index=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Signer.full_name'
        db.delete_column(u'django_docusign_demo_signer', 'full_name')

        # Deleting field 'Signer.email'
        db.delete_column(u'django_docusign_demo_signer', 'email')


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
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'db_index': 'True'}),
            'full_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'signature': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'signers'", 'to': u"orm['django_docusign_demo.Signature']"})
        }
    }

    complete_apps = ['django_docusign_demo']
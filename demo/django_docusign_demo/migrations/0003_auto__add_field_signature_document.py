# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Signature.document'
        db.add_column(u'django_docusign_demo_signature', 'document',
                      self.gf('django.db.models.fields.files.FileField')(max_length=100, null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Signature.document'
        db.delete_column(u'django_docusign_demo_signature', 'document')


    models = {
        u'django_docusign_demo.signature': {
            'Meta': {'object_name': 'Signature'},
            'document': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
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
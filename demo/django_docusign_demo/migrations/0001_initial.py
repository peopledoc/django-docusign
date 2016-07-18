# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import uuid

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Signature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('signature_backend_id', models.CharField(default='', max_length=100, verbose_name='ID for signature backend', db_index=True, blank=True)),
                ('anysign_internal_id', models.UUIDField(verbose_name='ID in internal database', default=uuid.uuid4)),
                ('document', models.FileField(upload_to=b'signatures', null=True, verbose_name='document', blank=True)),
                ('document_title', models.CharField(default='', max_length=100, verbose_name='title', blank=True)),
                ('status', models.CharField(default=b'draft', max_length=50, verbose_name='status', db_index=True, choices=[(b'draft', 'draft'), (b'sent', 'sent'), (b'delivered', 'delivered'), (b'completed', 'completed'), (b'declined', 'declined')])),
                ('status_datetime', models.DateTimeField(auto_now_add=True, verbose_name='status datetime')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SignatureType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('signature_backend_code', models.CharField(max_length=50, verbose_name='signature backend', db_index=True)),
                ('docusign_template_id', models.CharField(max_length=36, verbose_name='DocuSign template id', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Signer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('signing_order', models.PositiveSmallIntegerField(default=0, help_text='Position in the list of signers. Starts at 1.', verbose_name='signing order')),
                ('signature_backend_id', models.CharField(default='', max_length=100, verbose_name='ID in signature backend', db_index=True, blank=True)),
                ('anysign_internal_id', models.UUIDField(verbose_name='ID in internal database', default=uuid.uuid4)),
                ('full_name', models.CharField(max_length=50, verbose_name='full name', db_index=True)),
                ('email', models.EmailField(max_length=75, verbose_name='email', db_index=True)),
                ('status', models.CharField(default=b'draft', max_length=50, verbose_name='status', db_index=True, choices=[(b'draft', 'draft'), (b'sent', 'sent'), (b'delivered', 'delivered'), (b'completed', 'completed'), (b'declined', 'declined')])),
                ('status_datetime', models.DateTimeField(auto_now_add=True, verbose_name='status datetime')),
                ('status_details', models.CharField(max_length=250, verbose_name='status details', blank=True)),
                ('signature', models.ForeignKey(related_name='signers', to='django_docusign_demo.Signature')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='signature',
            name='signature_type',
            field=models.ForeignKey(verbose_name='signature type', to='django_docusign_demo.SignatureType'),
            preserve_default=True,
        ),
    ]

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase


from django_north.management import permissions


class PermissionTestCase(TestCase):
    def test_get_all_permissions(self):
        # this method is mocked in unit tests
        # test it for real
        bad_ct = ContentType.objects.create(
            app_label='myapp', model='mymodel1')
        Permission.objects.create(
            content_type=bad_ct, codename='badcodename', name='bad name')
        ct1 = ContentType.objects.get(app_label='north_app', model='author')
        ct2 = ContentType.objects.get(app_label='north_app', model='book')

        self.assertEquals(
            permissions.get_all_permissions([ct1, ct2]),
            set([
                (ct2.pk, u'change_book'), (ct2.pk, u'delete_book'),
                (ct2.pk, u'add_book'),
                (ct1.pk, u'change_author'), (ct1.pk, u'add_author'),
                (ct1.pk, u'delete_author'),
            ])
        )

        self.assertEquals(
            permissions.get_all_permissions([ct1]),
            set([
                (ct1.pk, u'change_author'), (ct1.pk, u'delete_author'),
                (ct1.pk, u'add_author'),
            ])
        )

        Permission.objects.get(codename='delete_author').delete()
        self.assertEquals(
            permissions.get_all_permissions([ct1]),
            set([
                (ct1.pk, u'change_author'), (ct1.pk, u'add_author'),
            ])
        )

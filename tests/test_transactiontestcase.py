from django.contrib.auth.models import Permission
from django.test import TransactionTestCase

from tests.north_app.models import Author
from tests.north_app.models import Book


class BookTestCase(TransactionTestCase):
    def setUp(self):
        self.author = Author.objects.create(name="George R. R. Martin")
        self.book1 = Book.objects.create(
            author=self.author,
            title="A Game of Thrones",
            pages=1234)
        self.book2 = Book.objects.create(
            author=self.author,
            title="A Clash of Kings",
            pages=1235)

    def test_delete_book(self):
        self.book1.delete()

        self.assertEquals(self.author.book_set.count(), 1)

    def test_permissions(self):
        # test that the correct fixtures where loaded:
        # schema inited in 0.1
        # 'add_author' permission created in 1.0
        # if the permission 'add_author' exists, it's ok
        self.assertTrue(
            Permission.objects.filter(codename='add_author').exists())

from django.test import TestCase

from tests.north_app.models import Author
from tests.north_app.models import Book


class BookTestCase(TestCase):
    def test_count_books(self):
        author = Author.objects.create(name="George R. R. Martin")
        Book.objects.create(
            author=author,
            title="A Game of Thrones",
            pages=1234)
        Book.objects.create(
            author=author,
            title="A Clash of Kings",
            pages=1235)

        self.assertEquals(author.book_set.count(), 2)

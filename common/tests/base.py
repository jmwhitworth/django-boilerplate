from django.core.cache import cache
from django.db import connection
from django.test import TestCase as DjangoTestCase

from common.tests.models import DummyModel


class TestCase(DjangoTestCase):
    def setUp(self):
        super().setUp()
        cache.clear()


class DummyModelTestCase(TestCase):
    """
    Base for tests that need a real `DummyModel` table. `DummyModel` has no
    migration, so its schema is created once for the class and dropped
    afterwards, rather than relying on the migration-built test database.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(DummyModel)

    @classmethod
    def tearDownClass(cls):
        with connection.schema_editor() as schema_editor:
            schema_editor.delete_model(DummyModel)

        super().tearDownClass()

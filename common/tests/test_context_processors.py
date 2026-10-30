from django.test import RequestFactory

from common.context_processors import environment
from common.tests.base import TestCase


class environment__TestCase(TestCase):
    def test_contains_expected_context(self):
        context = environment(RequestFactory().get("/"))
        self.assertIn("is_local", context)
        self.assertIn("is_production", context)
        self.assertIn("is_staging", context)
        self.assertIn("is_testing", context)

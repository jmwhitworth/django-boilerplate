from unittest.mock import patch

from django.conf import settings
from django.test import RequestFactory, override_settings

from common.tests.base import TestCase
from common.utils import (
    absolute_url,
    is_local,
    is_production,
    is_staging,
    is_testing,
)


class is_local__TestCase(TestCase):
    @patch.object(settings, "ENVIRONMENT", "LOCAL")
    def test_is_local_returns_true(self):
        self.assertTrue(is_local())

    @patch.object(settings, "ENVIRONMENT", "NOT_LOCAL")
    def test_is_local_returns_false(self):
        self.assertFalse(is_local())


class is_production__TestCase(TestCase):
    @patch.object(settings, "ENVIRONMENT", "PRODUCTION")
    def test_is_production_returns_true(self):
        self.assertTrue(is_production())

    @patch.object(settings, "ENVIRONMENT", "NOT_PRODUCTION")
    def test_is_production_returns_false(self):
        self.assertFalse(is_production())


class is_staging__TestCase(TestCase):
    @patch.object(settings, "ENVIRONMENT", "STAGING")
    def test_is_staging_returns_true(self):
        self.assertTrue(is_staging())

    @patch.object(settings, "ENVIRONMENT", "NOT_STAGING")
    def test_is_staging_returns_false(self):
        self.assertFalse(is_staging())


class is_testing__TestCase(TestCase):
    @patch.object(settings, "ENVIRONMENT", "TESTING")
    def test_is_testing_returns_true(self):
        self.assertTrue(is_testing())

    @patch.object(settings, "ENVIRONMENT", "NOT_TESTING")
    def test_is_testing_returns_false(self):
        self.assertFalse(is_testing())


class absolute_url__TestCase(TestCase):
    @override_settings(SITE_URL="https://foobar.example")
    def test_uses_site_url_when_set(self):
        request = RequestFactory().get("/", HTTP_HOST="localhost")
        self.assertEqual(absolute_url("/foo/", request), "https://foobar.example/foo/")

    @override_settings(SITE_URL="")
    def test_falls_back_to_request_host(self):
        request = RequestFactory().get("/", HTTP_HOST="localhost")
        self.assertEqual(absolute_url("/foo/", request), "http://localhost/foo/")

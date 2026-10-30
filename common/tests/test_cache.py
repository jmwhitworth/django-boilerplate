from django.core.cache import cache

from common.cache import CacheVersion
from common.tests.base import TestCase


class DummyCacheVersion(CacheVersion):
    prefix = "dummy_version"


class CacheVersion__TestCase(TestCase):
    def test_get_is_stable_until_bumped(self):
        self.assertEqual(DummyCacheVersion.get("a"), DummyCacheVersion.get("a"))

    def test_bump_changes_the_version(self):
        version = DummyCacheVersion.get("a")
        with self.captureOnCommitCallbacks(execute=True):
            DummyCacheVersion.bump("a")
        self.assertNotEqual(DummyCacheVersion.get("a"), version)

    def test_bump_waits_for_the_commit(self):
        version = DummyCacheVersion.get("a")
        with self.captureOnCommitCallbacks() as callbacks:
            DummyCacheVersion.bump("a")
            self.assertEqual(DummyCacheVersion.get("a"), version)
        for callback in callbacks:
            callback()
        self.assertNotEqual(DummyCacheVersion.get("a"), version)

    def test_bump_works_without_an_existing_version(self):
        with self.captureOnCommitCallbacks(execute=True):
            DummyCacheVersion.bump("a")
        self.assertIsNotNone(cache.get("dummy_version:a"))

    def test_bump_only_affects_its_own_identifier(self):
        other = DummyCacheVersion.get("b")
        with self.captureOnCommitCallbacks(execute=True):
            DummyCacheVersion.bump("a")
        self.assertEqual(DummyCacheVersion.get("b"), other)

    def test_a_lost_version_comes_back_later_than_before(self):
        with self.captureOnCommitCallbacks(execute=True):
            DummyCacheVersion.bump("a")
        version = DummyCacheVersion.get("a")
        cache.delete("dummy_version:a")
        self.assertGreater(DummyCacheVersion.get("a"), version)

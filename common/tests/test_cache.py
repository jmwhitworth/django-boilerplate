import uuid
from datetime import date, datetime
from functools import wraps
from unittest import mock

from django.core.cache import cache

from common.cache import CacheVersion, ttl_cache
from common.tests.base import TestCase
from common.tests.models import DummyModel


class DummyCacheVersion(CacheVersion):
    prefix = "dummy_version"


def _counting(func):
    """Wraps `func` so tests can see how many times the real function ran."""
    calls = []

    # wraps() keeps func's signature, which the cache decorators bind against
    @wraps(func)
    def counted(*args, **kwargs):
        calls.append((args, kwargs))
        return func(*args, **kwargs)

    return counted, calls


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

    def test_none_and_default_share_a_version(self):
        self.assertEqual(DummyCacheVersion.get(), DummyCacheVersion.get("default"))

    def test_a_model_and_its_pk_share_a_version(self):
        instance = DummyModel(id=uuid.uuid4())
        version = DummyCacheVersion.get(instance)
        with self.captureOnCommitCallbacks(execute=True):
            DummyCacheVersion.bump(instance.pk)
        self.assertNotEqual(DummyCacheVersion.get(instance), version)

    def test_bump_many_changes_every_version(self):
        a, b, c = (DummyCacheVersion.get(x) for x in "abc")
        with self.captureOnCommitCallbacks(execute=True):
            DummyCacheVersion.bump_many(["a", "b"])
        self.assertGreater(DummyCacheVersion.get("a"), a)
        self.assertGreater(DummyCacheVersion.get("b"), b)
        self.assertEqual(DummyCacheVersion.get("c"), c)

    def test_bump_many_waits_for_the_commit(self):
        version = DummyCacheVersion.get("a")
        with self.captureOnCommitCallbacks() as callbacks:
            DummyCacheVersion.bump_many(["a"])
        self.assertEqual(DummyCacheVersion.get("a"), version)
        self.assertEqual(len(callbacks), 1)

    def test_bump_many_with_nothing_does_nothing(self):
        with self.captureOnCommitCallbacks() as callbacks:
            DummyCacheVersion.bump_many([])
        self.assertEqual(callbacks, [])


class CacheVersion__cached__TestCase(TestCase):
    def test_caches_the_result(self):
        func, calls = _counting(lambda *, a: a * 2)
        cached = DummyCacheVersion.cached()(func)
        self.assertEqual(cached(a=2), 4)
        self.assertEqual(cached(a=2), 4)
        self.assertEqual(len(calls), 1)

    def test_bump_makes_the_result_stale(self):
        func, calls = _counting(lambda *, a: a)
        cached = DummyCacheVersion.cached()(func)
        cached(a=1)
        with self.captureOnCommitCallbacks(execute=True):
            DummyCacheVersion.bump()
        cached(a=1)
        self.assertEqual(len(calls), 2)

    def test_identifier_arg_scopes_the_version(self):
        func, calls = _counting(lambda *, owner, page: (owner, page))
        cached = DummyCacheVersion.cached(identifier_arg="owner")(func)
        cached(owner="a", page=1)
        cached(owner="b", page=1)
        with self.captureOnCommitCallbacks(execute=True):
            DummyCacheVersion.bump("a")
        cached(owner="a", page=1)
        cached(owner="b", page=1)
        self.assertEqual([kwargs["owner"] for _, kwargs in calls], ["a", "b", "a"])

    def test_identifier_arg_can_be_a_model(self):
        instance = DummyModel(id=uuid.uuid4())
        func, calls = _counting(lambda *, obj: obj.pk)
        cached = DummyCacheVersion.cached(identifier_arg="obj")(func)
        cached(obj=instance)
        with self.captureOnCommitCallbacks(execute=True):
            DummyCacheVersion.bump(instance)
        cached(obj=instance)
        self.assertEqual(len(calls), 2)

    def test_uses_the_timeout(self):
        func = DummyCacheVersion.cached(timeout=123)(lambda *, a: a)
        with mock.patch.object(cache, "set", wraps=cache.set) as cache_set:
            func(a=1)
        self.assertEqual(cache_set.call_args.kwargs["timeout"], 123)

    def test_vary_on_today_caches_each_day_separately(self):
        func, calls = _counting(lambda: 1)
        cached = DummyCacheVersion.cached(vary_on_today=True)(func)
        with mock.patch("common.cache.timezone.localdate") as localdate:
            localdate.return_value = date(2026, 3, 1)
            cached()
            cached()
            localdate.return_value = date(2026, 3, 2)
            cached()
        self.assertEqual(len(calls), 2)

    def test_without_vary_on_today_the_day_is_ignored(self):
        func, calls = _counting(lambda: 1)
        cached = DummyCacheVersion.cached()(func)
        with mock.patch("common.cache.timezone.localdate") as localdate:
            localdate.return_value = date(2026, 3, 1)
            cached()
            localdate.return_value = date(2026, 3, 2)
            cached()
        self.assertEqual(len(calls), 1)


class ttl_cache__TestCase(TestCase):
    def test_caches_the_result(self):
        func, calls = _counting(lambda *, a: a * 2)
        cached = ttl_cache(key_prefix="test")(func)
        self.assertEqual(cached(a=2), 4)
        self.assertEqual(cached(a=2), 4)
        self.assertEqual(len(calls), 1)

    def test_caches_a_none_result(self):
        func, calls = _counting(lambda: None)
        cached = ttl_cache(key_prefix="test")(func)
        self.assertIsNone(cached())
        self.assertIsNone(cached())
        self.assertEqual(len(calls), 1)

    def test_different_arguments_are_cached_separately(self):
        cached = ttl_cache(key_prefix="test")(lambda *, a: a)
        self.assertEqual(cached(a=1), 1)
        self.assertEqual(cached(a=2), 2)

    def test_positional_keyword_and_default_arguments_share_a_key(self):
        def func(a, b=2):
            return a + b

        counted, calls = _counting(func)
        cached = ttl_cache(key_prefix="test")(counted)
        cached(1)
        cached(1, 2)
        cached(a=1, b=2)
        self.assertEqual(len(calls), 1)

    def test_prefix_separates_functions_with_the_same_name(self):
        def func():
            return "first"

        first = ttl_cache(key_prefix="one")(func)

        def func():
            return "second"

        second = ttl_cache(key_prefix="two")(func)
        self.assertEqual(first(), "first")
        self.assertEqual(second(), "second")

    def test_uses_the_timeout(self):
        func = ttl_cache(key_prefix="test", timeout=123)(lambda: 1)
        with mock.patch.object(cache, "set", wraps=cache.set) as cache_set:
            func()
        self.assertEqual(cache_set.call_args.kwargs["timeout"], 123)

    def test_uncached_runs_the_real_function(self):
        func, calls = _counting(lambda: 1)
        cached = ttl_cache(key_prefix="test")(func)
        cached()
        cached.uncached()
        self.assertEqual(len(calls), 2)

    def test_vary_on_today_caches_each_day_separately(self):
        func, calls = _counting(lambda: 1)
        cached = ttl_cache(key_prefix="test", vary_on_today=True)(func)
        with mock.patch("common.cache.timezone.localdate") as localdate:
            localdate.return_value = date(2026, 3, 1)
            cached()
            cached()
            localdate.return_value = date(2026, 3, 2)
            cached()
        self.assertEqual(len(calls), 2)

    def test_without_vary_on_today_the_day_is_ignored(self):
        func, calls = _counting(lambda: 1)
        cached = ttl_cache(key_prefix="test")(func)
        with mock.patch("common.cache.timezone.localdate") as localdate:
            localdate.return_value = date(2026, 3, 1)
            cached()
            localdate.return_value = date(2026, 3, 2)
            cached()
        self.assertEqual(len(calls), 1)


class ttl_cache__cache_key__TestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.func, self.calls = _counting(lambda *, a: 1)
        self.cached = ttl_cache(key_prefix="test")(self.func)

    def test_supported_types_are_cached_separately(self):
        values = [
            "a",
            1,
            1.5,
            True,
            None,
            date(2026, 3, 1),
            datetime(2026, 3, 1, 12),
            uuid.uuid4(),
        ]
        for value in values:
            self.cached(a=value)
            self.cached(a=value)
        self.assertEqual(len(self.calls), len(values))

    def test_model_instances_with_the_same_pk_share_an_entry(self):
        pk = uuid.uuid4()
        self.cached(a=DummyModel(id=pk, name="a"))
        self.cached(a=DummyModel(id=pk, name="b"))
        self.assertEqual(len(self.calls), 1)

    def test_model_instances_with_different_pks_are_cached_separately(self):
        self.cached(a=DummyModel(id=uuid.uuid4()))
        self.cached(a=DummyModel(id=uuid.uuid4()))
        self.assertEqual(len(self.calls), 2)

    def test_model_without_a_pk_raises(self):
        with self.assertRaises(TypeError):
            self.cached(a=DummyModel(id=None))

    def test_unsupported_types_raise(self):
        for value in [[1], (1,), {"a": 1}, {1}, object()]:
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    self.cached(a=value)

    def test_queryset_raises_without_running_a_query(self):
        with self.assertNumQueries(0), self.assertRaises(TypeError):
            self.cached(a=DummyModel.objects.all())

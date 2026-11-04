import inspect
import time
from collections.abc import Callable, Iterable
from datetime import date
from functools import wraps
from typing import Any, ParamSpec, TypeVar
from uuid import UUID

from django.core.cache import cache
from django.db import transaction
from django.db.models import Model
from django.utils import timezone

from common.constants import ONE_DAY, ONE_MINUTE, ONE_YEAR

Identifier = str | UUID | date | Model | None
P = ParamSpec("P")
R = TypeVar("R")

_MISS = object()

# Types whose str() is unique and cheap, so safe to put in a cache key.
# datetime is a date subclass, and bool an int one.
_KEY_TYPES = (str, int, float, date, UUID, type(None))


def _key_part(value: Any) -> str:
    """
    Model instances are keyed by their pk, as their str() needn't be unique.
    Anything else, such as a QuerySet, raises rather than risk a key that
    collides, never hits, or runs a query.
    """
    if isinstance(value, Model):
        if value.pk is None:
            raise TypeError(f"Can't cache on an unsaved {type(value).__name__}.")
        return f"{value._meta.label_lower}#{value.pk}"
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, _KEY_TYPES):
        return str(value)
    raise TypeError(f"Can't use a {type(value).__name__} in a cache key.")


def _cached(
    func: Callable[P, R],
    *,
    prefix: str,
    timeout: int,
    version_for: Callable[[dict[str, Any]], int] | None = None,
    vary_on_today: bool = False,
) -> Callable[P, R]:
    """
    Caches `func` under a key built from its prefix, name and arguments, e.g.
    "analytics:promotions_by_date_get:start=2026-03-01:end=2026-03-07".
    """
    sig = inspect.signature(func)

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        parts = [f"{k}={_key_part(v)}" for k, v in bound.arguments.items()]
        if vary_on_today:
            parts.append(f"today={timezone.localdate()}")
        key = ":".join([prefix, func.__name__, *parts])
        version = version_for(bound.arguments) if version_for else None

        cached_val = cache.get(key, default=_MISS, version=version)
        if cached_val is not _MISS:
            return cached_val

        result = func(*args, **kwargs)
        cache.set(key, result, timeout=timeout, version=version)
        return result

    # Expose the raw function for tests or bypassing the cache
    wrapper.uncached = func  # type: ignore[attr-defined]
    return wrapper


class CacheVersion:
    """
    A version number to pass as `version=` when caching anything derived from
    one object, so bumping it makes those entries stale and lets them expire.

    Versions are nanosecond timestamps, so a new one is always later than any
    before it, even when the old one has expired or been evicted.
    """

    prefix: str

    @classmethod
    def _key(cls, identifier: Identifier = None) -> str:
        if identifier is None:
            identifier = "default"
        # By pk alone, so get(user) and bump(user.id) share a version
        if isinstance(identifier, Model):
            if identifier.pk is None:
                raise TypeError(
                    f"Can't cache on an unsaved {type(identifier).__name__}."
                )
            identifier = identifier.pk
        return f"{cls.prefix}:{_key_part(identifier)}"

    @classmethod
    def get(cls, identifier: Identifier = None) -> int:
        return cache.get_or_set(cls._key(identifier), time.time_ns, timeout=ONE_YEAR)

    @classmethod
    def bump(cls, identifier: Identifier = None) -> None:
        """
        Deferred until commit, otherwise a request in between could cache the
        old data under the new version.
        """
        transaction.on_commit(
            lambda: cache.set(cls._key(identifier), time.time_ns(), timeout=ONE_YEAR)
        )

    @classmethod
    def bump_many(cls, identifiers: Iterable[Identifier]) -> None:
        """Like bump, but sets every version in one cache round trip."""
        keys = [cls._key(identifier) for identifier in identifiers]
        if not keys:
            return
        transaction.on_commit(
            lambda: cache.set_many(
                dict.fromkeys(keys, time.time_ns()), timeout=ONE_YEAR
            )
        )

    @classmethod
    def cached(
        cls,
        *,
        timeout: int = ONE_DAY,
        identifier_arg: str | None = None,
        vary_on_today: bool = False,
    ) -> Callable[[Callable[P, R]], Callable[P, R]]:
        """
        Caches a selector's return value under this CacheVersion.
        If `identifier_arg` is provided, extracts that argument's value to scope the version.
        Pass `vary_on_today` for selectors that depend on today's date.
        """

        def version_for(arguments: dict[str, Any]) -> int:
            return cls.get(arguments[identifier_arg] if identifier_arg else None)

        def decorator(func: Callable[P, R]) -> Callable[P, R]:
            return _cached(
                func,
                prefix=cls.prefix,
                timeout=timeout,
                version_for=version_for,
                vary_on_today=vary_on_today,
            )

        return decorator


def ttl_cache(
    *, key_prefix: str, timeout: int = ONE_MINUTE, vary_on_today: bool = False
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Caches a function's return value for a fixed TTL timeout based on its arguments.
    Pass `vary_on_today` for functions that depend on today's date, so they
    don't serve yesterday's result after midnight.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        return _cached(
            func, prefix=key_prefix, timeout=timeout, vary_on_today=vary_on_today
        )

    return decorator

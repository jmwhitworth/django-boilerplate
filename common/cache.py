import time
from datetime import date
from uuid import UUID

from django.core.cache import cache
from django.db import transaction

from common.constants import ONE_MONTH

Identifier = str | UUID | date


class CacheVersion:
    """
    A version number to pass as `version=` when caching anything derived from
    one object, so bumping it makes those entries stale and lets them expire.

    Versions are nanosecond timestamps, so a new one is always later than any
    before it, even when the old one has expired or been evicted.
    """

    prefix: str

    @classmethod
    def _key(cls, identifier: Identifier) -> str:
        return f"{cls.prefix}:{identifier}"

    @classmethod
    def get(cls, identifier: Identifier) -> int:
        return cache.get_or_set(cls._key(identifier), time.time_ns, timeout=ONE_MONTH)

    @classmethod
    def bump(cls, identifier: Identifier) -> None:
        """
        Deferred until commit, otherwise a request in between could cache the
        old data under the new version.
        """
        transaction.on_commit(
            lambda: cache.set(cls._key(identifier), time.time_ns(), timeout=ONE_MONTH)
        )

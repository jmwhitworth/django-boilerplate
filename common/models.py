import uuid
from contextlib import contextmanager
from contextvars import ContextVar

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

_allow_signal_skipping = ContextVar("allow_signal_skipping", default=False)


@contextmanager
def allow_signal_skipping():
    token = _allow_signal_skipping.set(True)
    try:
        yield
    finally:
        _allow_signal_skipping.reset(token)


class SignalSafeQuerySet(models.QuerySet):
    def bulk_create(self, *args, **kwargs):
        self._check("bulk_create")
        return super().bulk_create(*args, **kwargs)

    def bulk_update(self, *args, **kwargs):
        self._check("bulk_update")
        return super().bulk_update(*args, **kwargs)

    def update(self, **kwargs):
        self._check("update")
        return super().update(**kwargs)

    def _check(self, method):
        if not _allow_signal_skipping.get():
            raise RuntimeError(
                f"{self.model.__name__}.{method}() skips signals. "
                "Use save() or wrap it in allow_signal_skipping()."
            )


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("ID"),
    )

    created_at = models.DateTimeField(db_index=True, default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

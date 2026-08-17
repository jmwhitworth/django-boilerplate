from django.db import models

from common.models import BaseModel


class DummyModel(BaseModel):
    """
    Concrete stand-in for `BaseModel`, used only to exercise `common.services`
    and `common.selectors` against a real table. Not part of any migration —
    its schema is created/dropped directly by the tests that need it.
    """

    name = models.CharField(max_length=255)
    is_public = models.BooleanField(default=False)
    related = models.ManyToManyField("self", blank=True)

    class Meta:
        app_label = "common"

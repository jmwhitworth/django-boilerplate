from common.selectors import get_object
from common.tests.base import DummyModelTestCase
from common.tests.models import DummyModel


class get_object__TestCase(DummyModelTestCase):
    def test_returns_matching_instance(self):
        instance = DummyModel.objects.create(name="Findable")

        result = get_object(DummyModel, pk=instance.pk)

        self.assertEqual(result, instance)

    def test_returns_none_when_missing(self):
        result = get_object(DummyModel, pk=999999)

        self.assertIsNone(result)

    def test_accepts_queryset(self):
        DummyModel.objects.create(name="Hidden", is_public=False)
        visible = DummyModel.objects.create(name="Visible", is_public=True)

        result = get_object(DummyModel.objects.filter(is_public=True), pk=visible.pk)

        self.assertEqual(result, visible)

    def test_queryset_excludes_non_matching(self):
        hidden = DummyModel.objects.create(name="Hidden", is_public=False)

        result = get_object(DummyModel.objects.filter(is_public=True), pk=hidden.pk)

        self.assertIsNone(result)

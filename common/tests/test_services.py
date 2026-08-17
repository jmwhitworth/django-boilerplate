from common.services import model_update
from common.tests.base import DummyModelTestCase
from common.tests.models import DummyModel


class model_update__TestCase(DummyModelTestCase):
    def test_updates_only_changed_fields(self):
        instance = DummyModel.objects.create(name="Original", is_public=False)

        instance, has_updated = model_update(
            instance=instance,
            fields=["name", "is_public"],
            data={"name": "Renamed", "is_public": True},
        )

        instance.refresh_from_db()
        self.assertTrue(has_updated)
        self.assertEqual(instance.name, "Renamed")
        self.assertTrue(instance.is_public)

    def test_no_op_when_data_matches_instance(self):
        instance = DummyModel.objects.create(name="Same", is_public=True)
        original_updated_at = instance.updated_at

        instance, has_updated = model_update(
            instance=instance,
            fields=["name", "is_public"],
            data={"name": "Same", "is_public": True},
        )

        self.assertFalse(has_updated)
        self.assertEqual(instance.updated_at, original_updated_at)

    def test_ignores_fields_missing_from_data(self):
        instance = DummyModel.objects.create(name="Keep me")

        instance, has_updated = model_update(
            instance=instance, fields=["name", "is_public"], data={"name": "Keep me"}
        )

        self.assertFalse(has_updated)

    def test_raises_for_field_not_on_model(self):
        instance = DummyModel.objects.create(name="Test")

        with self.assertRaises(AssertionError):
            model_update(
                instance=instance,
                fields=["not_a_real_field"],
                data={"not_a_real_field": "value"},
            )

    def test_bumps_updated_at_on_change(self):
        instance = DummyModel.objects.create(name="Old")
        original_updated_at = instance.updated_at

        instance, has_updated = model_update(
            instance=instance, fields=["name"], data={"name": "New"}
        )
        instance.refresh_from_db()

        self.assertTrue(has_updated)
        self.assertGreater(instance.updated_at, original_updated_at)

    def test_updates_m2m_field(self):
        instance = DummyModel.objects.create(name="Parent")
        related = DummyModel.objects.create(name="Child")

        instance, has_updated = model_update(
            instance=instance, fields=["related"], data={"related": [related]}
        )

        self.assertTrue(has_updated)
        self.assertEqual(list(instance.related.all()), [related])

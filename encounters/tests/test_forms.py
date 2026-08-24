import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from encounters.forms import Open_Encounter_Form, ampmDateTimeInput, export_options_form
from encounters.models import Animal, Animal_Type


class AmpmDateTimeInputTests(TestCase):
    def setUp(self):
        self.widget = ampmDateTimeInput(format='%m/%d/%Y  %I:%M %p')

    def test_parses_expected_format(self):
        value = self.widget.value_from_datadict({'when': '08/24/2026  10:00 AM'}, {}, 'when')
        self.assertEqual(value, datetime.datetime(2026, 8, 24, 10, 0))

    def test_unparseable_value_returned_as_is(self):
        value = self.widget.value_from_datadict({'when': 'not-a-date'}, {}, 'when')
        self.assertEqual(value, 'not-a-date')

    def test_missing_value_does_not_crash(self):
        value = self.widget.value_from_datadict({}, {}, 'when')
        self.assertIsNone(value)


class OpenEncounterFormTests(TestCase):
    def setUp(self):
        animal_type = Animal_Type.objects.create(animal_type='Bird')
        self.animal = Animal.objects.create(Name='Kevin', Animal_Type=animal_type)
        self.user = get_user_model().objects.create_user(username='handler', password='pw')

    def test_valid_data(self):
        form = Open_Encounter_Form(data={
            'encounter_date': '08/24/2026  10:00 AM',
            'animal': self.animal.pk,
            'user': self.user.pk,
        })
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_required_fields(self):
        form = Open_Encounter_Form(data={})
        self.assertFalse(form.is_valid())
        for field in ('encounter_date', 'animal', 'user'):
            self.assertIn(field, form.errors)


class ExportOptionsFormTests(TestCase):
    def test_all_fields_optional(self):
        form = export_options_form(data={})
        self.assertTrue(form.is_valid(), form.errors)

import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from encounters.forms import Open_Encounter_Form, export_options_form
from encounters.models import Animal, Animal_Type


class OpenEncounterFormTests(TestCase):
    def setUp(self):
        animal_type = Animal_Type.objects.create(animal_type='Bird')
        self.animal = Animal.objects.create(Name='Kevin', Animal_Type=animal_type)
        self.user = get_user_model().objects.create_user(username='handler', password='pw')

    def test_valid_data(self):
        form = Open_Encounter_Form(data={
            'encounter_date': '2026-08-24T10:00',  # format an <input type=datetime-local> submits
            'animal': self.animal.pk,
            'user': self.user.pk,
        })
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data['encounter_date'], datetime.datetime(2026, 8, 24, 10, 0))

    def test_missing_required_fields(self):
        form = Open_Encounter_Form(data={})
        self.assertFalse(form.is_valid())
        for field in ('encounter_date', 'animal', 'user'):
            self.assertIn(field, form.errors)


class ExportOptionsFormTests(TestCase):
    def test_all_fields_optional(self):
        form = export_options_form(data={})
        self.assertTrue(form.is_valid(), form.errors)

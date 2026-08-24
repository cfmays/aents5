from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from encounters.models import Animal, Animal_Type, Encounter


class AnimalTypeModelTests(TestCase):
    def test_str(self):
        animal_type = Animal_Type.objects.create(animal_type='Reptile')
        self.assertEqual(str(animal_type), 'Reptile')


class AnimalModelTests(TestCase):
    def setUp(self):
        self.animal_type = Animal_Type.objects.create(animal_type='Reptile')
        self.animal = Animal.objects.create(Name='Sheldon', Animal_Type=self.animal_type)
        self.user = get_user_model().objects.create_user(username='handler', password='pw')

    def test_str(self):
        self.assertEqual(str(self.animal), 'Reptile Sheldon')

    def test_todays_encounters_counts_only_recent(self):
        Encounter.objects.create(encounter_date=timezone.now(), animal=self.animal, user=self.user)
        Encounter.objects.create(
            encounter_date=timezone.now() - timedelta(days=5), animal=self.animal, user=self.user
        )
        self.assertEqual(self.animal.todays_encounters(), 1)

    def test_soft_deleted_animal_excluded_from_default_manager(self):
        self.animal.delete()
        self.assertEqual(Animal.objects.count(), 0)
        self.assertEqual(Animal.all_objects.count(), 1)


class EncounterModelTests(TestCase):
    def setUp(self):
        animal_type = Animal_Type.objects.create(animal_type='Bird')
        self.animal = Animal.objects.create(Name='Kevin', Animal_Type=animal_type)
        self.user = get_user_model().objects.create_user(username='handler', password='pw')

    def test_str_with_user_and_animal(self):
        encounter = Encounter.objects.create(
            encounter_date=timezone.now(), animal=self.animal, user=self.user
        )
        self.assertEqual(str(encounter), 'handler/Kevin')

    def test_animal_is_required(self):
        encounter = Encounter(encounter_date=timezone.now(), user=self.user)
        with self.assertRaises(ValidationError):
            encounter.full_clean()

    def test_user_is_required(self):
        encounter = Encounter(encounter_date=timezone.now(), animal=self.animal)
        with self.assertRaises(ValidationError):
            encounter.full_clean()

    def test_saving_without_animal_is_rejected_by_the_database(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Encounter.objects.create(encounter_date=timezone.now(), user=self.user)

    def test_saving_without_user_is_rejected_by_the_database(self):
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                Encounter.objects.create(encounter_date=timezone.now(), animal=self.animal)

    def test_deleting_a_user_with_encounters_is_protected(self):
        Encounter.objects.create(encounter_date=timezone.now(), animal=self.animal, user=self.user)
        with transaction.atomic():
            with self.assertRaises(IntegrityError):
                self.user.delete()

    def test_get_absolute_url(self):
        encounter = Encounter.objects.create(
            encounter_date=timezone.now(), animal=self.animal, user=self.user
        )
        self.assertEqual(encounter.get_absolute_url(), f'/encounters/encounter/{encounter.pk}')

    def test_get_total_minutes_sums_provided_times(self):
        encounter = Encounter.objects.create(
            encounter_date=timezone.now(), animal=self.animal, user=self.user,
            handling_time=10, crate_time=5, holding_time=3,
        )
        self.assertEqual(encounter.get_total_minutes(), 18)

    def test_get_total_minutes_falls_back_to_elapsed_when_no_times_logged(self):
        encounter = Encounter.objects.create(
            encounter_date=timezone.now() - timedelta(minutes=10),
            animal=self.animal, user=self.user,
            handling_time=0, crate_time=0, holding_time=0,
        )
        self.assertAlmostEqual(encounter.get_total_minutes(), 10, delta=1)

    def test_get_total_minutes_treats_none_times_as_zero(self):
        encounter = Encounter.objects.create(
            encounter_date=timezone.now() - timedelta(minutes=10),
            animal=self.animal, user=self.user,
            handling_time=None, crate_time=None, holding_time=None,
        )
        self.assertAlmostEqual(encounter.get_total_minutes(), 10, delta=1)

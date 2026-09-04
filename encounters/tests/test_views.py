import csv
import io
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from encounters.models import Animal, Animal_Type, Encounter


class ViewTestBase(TestCase):
    def setUp(self):
        self.animal_type = Animal_Type.objects.create(animal_type='Bird')
        self.animal = Animal.objects.create(Name='Kevin', Animal_Type=self.animal_type)
        self.user = get_user_model().objects.create_user(username='handler', password='pw')
        self.encounter = Encounter.objects.create(
            encounter_date=timezone.now(), animal=self.animal, user=self.user,
        )


class InactiveUserLoginTests(ViewTestBase):
    def test_active_user_can_log_in(self):
        logged_in = self.client.login(username='handler', password='pw')
        self.assertTrue(logged_in)

    def test_inactive_user_cannot_log_in(self):
        self.user.is_active = False
        self.user.save()
        logged_in = self.client.login(username='handler', password='pw')
        self.assertFalse(logged_in)

    def test_inactive_user_post_to_login_view_is_rejected(self):
        self.user.is_active = False
        self.user.save()
        response = self.client.post(reverse('login'), data={'username': 'handler', 'password': 'pw'})
        self.assertEqual(response.status_code, 200)  # re-renders the login form with an error
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_user_with_encounters_can_still_be_deactivated(self):
        # unlike delete() (blocked by on_delete=PROTECT), deactivating is how
        # you keep a handler with encounter history from logging in again
        self.user.is_active = False
        self.user.save()
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)


class IndexViewTests(ViewTestBase):
    def test_index_shows_counts(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['num_animals'], 1)
        self.assertEqual(response.context['num_users'], 1)
        self.assertEqual(response.context['num_encounters'], 1)


class OpenEncounterViewTests(ViewTestBase):
    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(reverse('openencounter'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response.url)

    def test_logged_in_user_sees_form(self):
        self.client.login(username='handler', password='pw')
        response = self.client.get(reverse('openencounter'))
        self.assertEqual(response.status_code, 200)

    def test_valid_post_creates_encounter(self):
        self.client.login(username='handler', password='pw')
        response = self.client.post(reverse('openencounter'), data={
            'encounter_date': '2026-08-24T09:00',
            'animal': self.animal.pk,
            'user': self.user.pk,
            'participation': 'participated',
        })
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Encounter.objects.count(), 2)


class EncountersByUserListViewTests(ViewTestBase):
    def test_requires_login(self):
        response = self.client.get(reverse('my-encounters'))
        self.assertEqual(response.status_code, 302)

    def test_only_shows_own_encounters(self):
        other_user = get_user_model().objects.create_user(username='other', password='pw')
        Encounter.objects.create(encounter_date=timezone.now(), animal=self.animal, user=other_user)

        self.client.login(username='handler', password='pw')
        response = self.client.get(reverse('my-encounters'))
        self.assertEqual(list(response.context['encounter_list']), [self.encounter])


class AllEncountersListViewTests(ViewTestBase):
    def test_lists_all_encounters(self):
        response = self.client.get(reverse('all-encounters'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['encounter_list']), [self.encounter])


class TodaysEncountersListViewTests(ViewTestBase):
    def test_only_shows_future_encounters(self):
        # the view filters encounter_date__gt=today's date, so only today/future encounters match
        past_encounter = Encounter.objects.create(
            encounter_date=timezone.now() - timedelta(days=2), animal=self.animal, user=self.user,
        )
        response = self.client.get(reverse('todays-encounters'))
        encounters = list(response.context['encounter_list'])
        self.assertIn(self.encounter, encounters)
        self.assertNotIn(past_encounter, encounters)


class EncounterDetailViewTests(ViewTestBase):
    def test_get_renders_update_form(self):
        response = self.client.get(reverse('encounter-detail', kwargs={'pk': self.encounter.pk}))
        self.assertEqual(response.status_code, 200)

    def test_post_updates_encounter(self):
        self.client.login(username='handler', password='pw')
        response = self.client.post(
            reverse('encounter-detail', kwargs={'pk': self.encounter.pk}),
            data={
                'encounter_date': '2026-08-24T09:00',
                'animal': self.animal.pk,
                'user': self.user.pk,
                'handling_time': 15,
                'crate_time': 0,
                'holding_time': 0,
                'comments': 'all done',
            },
        )
        self.assertRedirects(response, reverse('my-encounters'))
        self.encounter.refresh_from_db()
        self.assertEqual(self.encounter.handling_time, 15)
        self.assertEqual(self.encounter.comments, 'all done')


class AnimalTypesViewTests(ViewTestBase):
    def test_lists_animal_types(self):
        response = self.client.get(reverse('animal-types'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['animal_type_list']), [self.animal_type])


class AnimalTypesDetailViewTests(ViewTestBase):
    def test_filters_animals_by_type(self):
        other_type = Animal_Type.objects.create(animal_type='Reptile')
        Animal.objects.create(Name='Sheldon', Animal_Type=other_type)

        response = self.client.get(reverse('animallist', kwargs={'animal_type': 'Bird'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['animal_list']), [self.animal])


class EncountersByAnimalListViewTests(ViewTestBase):
    def test_filters_encounters_by_animal(self):
        other_animal = Animal.objects.create(Name='Ollie', Animal_Type=self.animal_type)
        Encounter.objects.create(encounter_date=timezone.now(), animal=other_animal, user=self.user)

        response = self.client.get(reverse('encounters-by-animal', kwargs={'pk': self.animal.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(list(response.context['encounter_list']), [self.encounter])


class LoadAnimalUsesViewTests(ViewTestBase):
    def test_returns_usage_json(self):
        response = self.client.get(reverse('animal-data-API'), {'animal': self.animal.pk})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['uses'], 1)
        self.assertEqual(data['theMax'], self.animal.Max_Daily)


class LoadAnimalsViewTests(ViewTestBase):
    def test_returns_animals_for_type(self):
        response = self.client.get(reverse('ajax_load_animals'), {'theAnimalTypeID': self.animal_type.pk})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Kevin')


class ExportDataViewTests(ViewTestBase):
    def test_returns_csv_with_encounter_row(self):
        response = self.client.get(reverse('export'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        rows = list(csv.reader(io.StringIO(response.content.decode())))
        self.assertEqual(rows[0], ['Date/Time', 'Animal', 'User', 'Handling Time', 'Crate Time', 'Holding time', 'Comments'])
        self.assertEqual(len(rows), 2)


class ExportOptionsViewTests(ViewTestBase):
    def test_get_renders_form(self):
        response = self.client.get(reverse('export-options'))
        self.assertEqual(response.status_code, 200)

    def test_post_filters_by_user(self):
        other_user = get_user_model().objects.create_user(username='other', password='pw')
        Encounter.objects.create(encounter_date=timezone.now(), animal=self.animal, user=other_user)

        response = self.client.post(reverse('export-options'), data={'users': other_user.pk})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        rows = list(csv.reader(io.StringIO(response.content.decode())))
        self.assertEqual(len(rows), 2)  # header + one matching encounter
        self.assertIn('other', rows[1][2])


class LogoutViewTests(ViewTestBase):
    def test_logout_redirects_and_clears_session(self):
        self.client.login(username='handler', password='pw')
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('my-encounters'), target_status_code=302)
        response = self.client.get(reverse('my-encounters'))
        self.assertEqual(response.status_code, 302)  # no longer logged in

from django.test import TestCase
from apps.service.tests import helpers
from apps.service.models import TelegramUsers, OutlineVPNKeys
from django.db.utils import IntegrityError


class TelegramUsersTestCase(TestCase):
    def test_create_telegram_users(self):
        users_to_create = 100
        self.assertEqual(users_to_create, len(helpers.create_telegram_users(users_to_create)))
        self.assertEqual(users_to_create, len(TelegramUsers.objects.all()))

    def test_uniq_constraint(self):
        helpers.create_telegram_users()
        with self.assertRaises(IntegrityError) as err:
            helpers.create_telegram_users()
        self.assertIn('unique_telegram_id', str(err.exception))


class OutlineVPNKeysTestCase(TestCase):
    def test_create_vpn_keys(self):
        keys_to_create = 100
        self.assertEqual(keys_to_create, len(helpers.create_vpn_keys(keys_to_create)))
        self.assertEqual(keys_to_create, len(OutlineVPNKeys.objects.all()))

import datetime
from django.test import TestCase
from apps.outline_vpn_admin.tests import helpers
from apps.outline_vpn_admin.models import TelegramUsers, OutlineVPNKeys
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

    def test_change_is_admin(self):
        tg_user = helpers.create_telegram_users()[0]
        self.assertFalse(tg_user.is_admin)
        tg_user.change_is_admin()
        self.assertTrue(tg_user.is_admin)
        tg_user.change_is_admin()
        self.assertFalse(tg_user.is_admin)


class OutlineVPNKeysTestCase(TestCase):
    def test_create_vpn_keys(self):
        keys_to_create = 100
        self.assertEqual(keys_to_create, len(helpers.create_vpn_keys(keys_to_create)))
        self.assertEqual(keys_to_create, len(OutlineVPNKeys.objects.all()))

    def test_add_tg_user(self):
        vpn_key = helpers.create_vpn_keys()[0]
        tg_user = helpers.create_telegram_users()[0]
        self.assertIsNone(vpn_key.telegram_user_record)
        vpn_key.add_tg_user(tg_user)
        self.assertIsNotNone(vpn_key.telegram_user_record)
        self.assertEqual(tg_user, vpn_key.telegram_user_record)

    def test_change_active_status(self):
        vpn_key = helpers.create_vpn_keys()[0]
        self.assertFalse(vpn_key.outline_key_active)
        vpn_key.change_active_status()
        self.assertTrue(vpn_key.outline_key_active)
        vpn_key.change_active_status()
        self.assertFalse(vpn_key.outline_key_active)

    def test_change_valid_until(self):
        vpn_key = helpers.create_vpn_keys()[0]
        self.assertIsNotNone(vpn_key.outline_key_valid_until)
        vpn_key.change_valid_until(0)
        self.assertIsNone(vpn_key.outline_key_valid_until)
        vpn_key.change_valid_until(10)
        self.assertIsNotNone(vpn_key.outline_key_valid_until)
        from_method = vpn_key.change_valid_until(50)
        self.assertIsInstance(from_method, datetime.datetime)
        from_method = vpn_key.change_valid_until(0)
        self.assertIsNone(from_method)

    def test_uniq_constraint_vpn(self):
        helpers.create_vpn_keys()
        with self.assertRaises(IntegrityError) as err:
            helpers.create_vpn_keys()
        self.assertIn('unique_outline_key_id', str(err.exception))

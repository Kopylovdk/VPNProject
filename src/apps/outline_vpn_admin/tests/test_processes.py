from unittest.mock import patch
from django.test import TestCase
from apps.outline_vpn_admin.models import TelegramUsers, OutlineVPNKeys
from telebot.types import User
from outline_vpn_admin_bot import bot_exceptions
import apps.outline_vpn_admin.processes as processes
import apps.outline_vpn_admin.tests.helpers as helpers


class MockResponseCreateKey:

    def __init__(self):
        self.status_code = 201

    def json(self):
        return {
            "id": 123,
            "name": "test",
            "password": "test",
            "port": 7000,
            "method": "test",
            "accessUrl": "test",
        }


class MockResponseStatusCode204:
    status_code = 204


class MockResponseStatusCode404:
    status_code = 404


class ValidateTestCase(TestCase):
    def test_validate_int_ok(self):
        self.assertTrue(processes.validate_int('1'))

    def test_validate_int_error(self):
        self.assertIsInstance(processes.validate_int('qwerty'), str)


class AddNewTGUserTestCase(TestCase):
    def setUp(self) -> None:
        self.tg_user = User(
            id=1000,
            is_bot=False,
            first_name='tg first_name test_1000',
            username='tg login test_1000',
            last_name='tg last_name update'
        )

    def test_add_new_tg_user(self):
        self.assertEqual(0, len(TelegramUsers.objects.all()))
        processes.add_new_tg_user(self.tg_user)
        new_user = TelegramUsers.objects.first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.telegram_id, self.tg_user.id)
        self.assertEqual(new_user.telegram_login, self.tg_user.username)
        self.assertEqual(new_user.telegram_first_name, self.tg_user.first_name)
        self.assertEqual(new_user.telegram_last_name, self.tg_user.last_name)

    def test_update_tg_user(self):
        helpers.create_telegram_users()
        processes.add_new_tg_user(self.tg_user)
        updated_user = TelegramUsers.objects.first()
        self.assertEqual(updated_user.telegram_last_name, self.tg_user.last_name)


class GetAllAdminsTestCase(TestCase):
    def test_get_all_admins(self):
        tg_users = helpers.create_telegram_users(5)
        tg_users[0].is_admin = True
        tg_users[0].save()
        tg_users[3].is_admin = True
        tg_users[3].save()
        check_data = processes.get_all_admins()
        self.assertEqual(2, len(check_data))
        self.assertEqual([1000, 1003], check_data)


class GetOutlineKeyByIdTestCase(TestCase):
    def test_get_outline_key_by_id_ok(self):
        vpn_keys = helpers.create_vpn_keys(3)
        from_db = processes.get_outline_key_by_id(vpn_keys[1].outline_key_id)
        self.assertIsInstance(from_db, OutlineVPNKeys)
        self.assertEqual(vpn_keys[1], from_db)

    def test_get_outline_key_by_id_not_found(self):
        self.assertEqual(bot_exceptions.OUTLINE_VPN_KEY_NOT_FOUND, processes.get_outline_key_by_id('1'))

    def test_get_outline_key_by_id_not_integer(self):
        self.assertEqual(bot_exceptions.NOT_INTEGER, processes.get_outline_key_by_id('qwerty'))


class GetTgUserByTestCase(TestCase):
    def setUp(self) -> None:
        self.tg_users = helpers.create_telegram_users(5)

    def test_get_tg_user_by_telegram_login(self):
        from_db = processes.get_tg_user_by_(telegram_data=self.tg_users[2].telegram_login)
        self.assertIsInstance(from_db, TelegramUsers)
        self.assertEqual(self.tg_users[2], from_db)

    def test_get_tg_user_by_telegram_id(self):
        from_db = processes.get_tg_user_by_(telegram_data=self.tg_users[1].telegram_id)
        self.assertIsInstance(from_db, TelegramUsers)
        self.assertEqual(self.tg_users[1], from_db)

    def test_get_tg_user_by_not_found(self):
        self.assertEqual(bot_exceptions.TELEGRAM_USER_NOT_FOUND, processes.get_tg_user_by_(15))


class GetAllNoAdminUsersTestCase(TestCase):
    def test_get_all_no_admin_users(self):
        tg_users = helpers.create_telegram_users(50)
        no_admins = processes.get_all_no_admin_users()
        self.assertEqual(len(no_admins), 50)
        tg_users[0].is_admin = True
        tg_users[0].save()
        tg_users[1].is_admin = True
        tg_users[1].save()
        no_admins = processes.get_all_no_admin_users()
        self.assertEqual(len(no_admins), 48)


class GetAllVPNKeysOfUserTestCase(TestCase):
    def test_get_all_vpn_keys_of_user(self):
        tg_user = helpers.create_telegram_users()[0]
        vpn_keys = helpers.create_vpn_keys(6)
        vpn_keys[0].telegram_user_record = tg_user
        vpn_keys[0].save()
        vpn_keys[1].telegram_user_record = tg_user
        vpn_keys[1].save()
        user_keys_by_login = processes.get_all_vpn_keys_of_user(user_data=tg_user.telegram_login)
        self.assertEqual(3, len(user_keys_by_login))
        user_keys_by_telegram_id = processes.get_all_vpn_keys_of_user(user_data=tg_user.telegram_id)
        self.assertEqual(3, len(user_keys_by_telegram_id))

    def test_get_all_vpn_keys_of_user_user_not_found(self):
        user_keys_by_login = processes.get_all_vpn_keys_of_user(user_data='some value')
        self.assertEqual(user_keys_by_login, bot_exceptions.TELEGRAM_USER_NOT_FOUND)

    def test_get_all_vpn_keys_of_user_no_vpns(self):
        tg_user = helpers.create_telegram_users()[0]
        user_keys_by_login = processes.get_all_vpn_keys_of_user(user_data=tg_user.telegram_login)
        self.assertIsInstance(user_keys_by_login, list)
        self.assertEqual(0, len(user_keys_by_login))


class AddNewVPNKeyTestCase(TestCase):
    @patch("requests.post", return_value=MockResponseCreateKey())
    def test_add_new_key_ok(self, mocked):
        vpn_key = processes.create_new_key('kz')
        from_db = OutlineVPNKeys.objects.all()
        self.assertIsInstance(vpn_key, OutlineVPNKeys)
        self.assertEqual(1, len(from_db))
        self.assertEqual(vpn_key.outline_key_name, from_db[0].outline_key_name)

    @patch("requests.post", return_value=MockResponseStatusCode404())
    def test_add_new_key_error(self, mocked):
        with self.assertRaises(Exception) as err:
            processes.create_new_key('kz')
        self.assertIn("Unable to create key", str(err.exception))
        from_db = OutlineVPNKeys.objects.all()
        self.assertEqual(0, len(from_db))


class AddTrafficLimitTestCase(TestCase):
    @patch("requests.put", return_value=MockResponseStatusCode204)
    def test_add_traffic_limit_true(self, mocked):
        vpn_key = helpers.create_vpn_keys()[0]
        response = processes.add_traffic_limit('kz', vpn_key)
        self.assertTrue(response)
        vpn_key.refresh_from_db()
        self.assertIsNotNone(vpn_key.outline_key_traffic_limit)

    @patch("requests.put", return_value=MockResponseStatusCode404)
    def test_add_traffic_limit_false(self, mocked):
        vpn_key = helpers.create_vpn_keys()[0]
        response = processes.add_traffic_limit('kz', vpn_key)
        self.assertFalse(response)
        vpn_key.refresh_from_db()
        self.assertIsNone(vpn_key.outline_key_traffic_limit)


class DelTrafficLimitTestCase(TestCase):
    @patch("requests.delete", return_value=MockResponseStatusCode204)
    def test_del_traffic_limit_true(self, mocked):
        vpn_key = helpers.create_vpn_keys()[0]
        vpn_key.outline_key_traffic_limit = 2000
        vpn_key.save()
        response = processes.del_traffic_limit('kz', vpn_key)
        self.assertTrue(response)
        vpn_key.refresh_from_db()
        self.assertIsNone(vpn_key.outline_key_traffic_limit)

    @patch("requests.delete", return_value=MockResponseStatusCode404)
    def test_del_traffic_limit_false(self, mocked):
        vpn_key = helpers.create_vpn_keys()[0]
        vpn_key.outline_key_traffic_limit = 2000
        vpn_key.save()
        response = processes.del_traffic_limit('kz', vpn_key)
        self.assertFalse(response)
        vpn_key.refresh_from_db()
        self.assertIsNotNone(vpn_key.outline_key_traffic_limit)


class DelOutlineVPNKeyTestCase(TestCase):
    @patch("requests.delete", return_value=MockResponseStatusCode204)
    def test_del_outline_vpn_key_true(self, mocked):
        response = processes.del_outline_vpn_key('kz', helpers.create_vpn_keys()[0])
        self.assertTrue(response)
        vpn_keys = OutlineVPNKeys.objects.all()
        self.assertEqual(0, len(vpn_keys))

    @patch("requests.delete", return_value=MockResponseStatusCode404)
    def test_del_outline_vpn_key_false(self, mocked):
        response = processes.del_outline_vpn_key('kz', helpers.create_vpn_keys()[0])
        self.assertFalse(response)
        vpn_keys = OutlineVPNKeys.objects.all()
        self.assertEqual(1, len(vpn_keys))


class ChangeOutlineVPNKeyNameTestCase(TestCase):
    @patch("requests.put", return_value=MockResponseStatusCode204)
    def test_change_outline_vpn_key_name_true(self, mocked):
        vpn_key = helpers.create_vpn_keys()[0]
        self.assertEqual(vpn_key.outline_key_name, "test_1000")
        response = processes.change_outline_vpn_key_name('kz', vpn_key, 'updated_test')
        self.assertTrue(response)
        vpn_key.refresh_from_db()
        self.assertEqual(vpn_key.outline_key_name, 'updated_test')

    @patch("requests.put", return_value=MockResponseStatusCode404)
    def test_change_outline_vpn_key_name_false(self, mocked):
        vpn_key = helpers.create_vpn_keys()[0]
        self.assertEqual(vpn_key.outline_key_name, "test_1000")
        response = processes.change_outline_vpn_key_name('kz', vpn_key, 'updated_test')
        self.assertFalse(response)
        vpn_key.refresh_from_db()
        self.assertIsNotNone(vpn_key.outline_key_name)
        self.assertEqual(vpn_key.outline_key_name, "test_1000")

from django.test import TestCase
from apps.service import exceptions
from apps.service.models import TelegramUsers, OutlineVPNKeys
from telebot.types import User
from apps.service.bot import bot_exceptions
import apps.service.processes as processes
import apps.service.tests.helpers as helpers


class ValidateTestCase(TestCase):
    def test_validate_int(self):
        self.assertTrue(processes._validate_int('1'))
        self.assertFalse(processes._validate_int('qwerty'))


class AddNewTGUserTestCase(TestCase):
    def setUp(self) -> None:
        self.tg_user = User(
            id=1,
            is_bot=False,
            first_name='tg first_name test_1',
            username='tg login test_1',
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
        self.assertEqual([1, 4], check_data)


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
    def test_add_new_key(self):
        vpn_key = processes.add_new_key(test=True)
        from_db = OutlineVPNKeys.objects.all()
        self.assertIsInstance(vpn_key, OutlineVPNKeys)
        self.assertEqual(1, len(from_db))
        self.assertEqual(vpn_key.outline_key_name, from_db[0].outline_key_name)

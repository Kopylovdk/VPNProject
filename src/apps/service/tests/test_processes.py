import datetime
from django.test import TestCase
from apps.service import exceptions
from apps.service.models import TelegramUsers, OutlineVPNKeys
from telebot.types import User
import apps.service.processes as processes
import apps.service.tests.helpers as helpers


class AddNewTGUserTestCase(TestCase):
    def setUp(self) -> None:
        self.tg_user = User(
            id=0,
            is_bot=False,
            first_name='tg first_name test_0',
            username='tg login test_0',
            last_name='tg last_name test_0'
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

    def test_add_new_tg_user_error(self):
        self.tg_user.id = 'asd'
        with self.assertRaises(exceptions.ProcessException) as err:
            processes.add_new_tg_user(self.tg_user)
        self.assertIn('Ошибка записи строки в БД', str(err.exception))


class GetAllAdminsTestCase(TestCase):
    def test_get_all_admins(self):
        tg_users = helpers.create_telegram_users(5)
        tg_users[0].is_admin = True
        tg_users[0].save()
        tg_users[3].is_admin = True
        tg_users[3].save()
        check_data = processes.get_all_admins()
        self.assertEqual(2, len(check_data))
        self.assertEqual(0, check_data[0])
        self.assertEqual(3, check_data[1])


class GetOutlineKeyByIdTestCase(TestCase):
    def test_get_outline_key_by_id_ok(self):
        vpn_keys = helpers.create_vpn_keys(3)
        from_db = processes.get_outline_key_by_id(vpn_keys[1].outline_key_id)
        self.assertIsInstance(from_db, OutlineVPNKeys)
        self.assertEqual(vpn_keys[1], from_db)

    def test_get_outline_key_by_id_none(self):
        self.assertIsNone(processes.get_outline_key_by_id(1))


class GetTgUserByTestCase(TestCase):
    def setUp(self) -> None:
        self.tg_users = helpers.create_telegram_users(5)

    def test_get_tg_user_by_telegram_login(self):
        from_db = processes.get_tg_user_by_(telegram_login=self.tg_users[2].telegram_login)
        self.assertIsInstance(from_db, TelegramUsers)
        self.assertEqual(self.tg_users[2], from_db)

    def test_get_tg_user_by_telegram_id(self):
        from_db = processes.get_tg_user_by_(telegram_id=self.tg_users[1].telegram_id)
        self.assertIsInstance(from_db, TelegramUsers)
        self.assertEqual(self.tg_users[1], from_db)


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


class AddNewVPNKeyToTGUserTestCase(TestCase):
    def test_add_new_vpn_key_to_tg_user(self):
        tg_users = helpers.create_telegram_users(3)
        processes.add_new_vpn_key_to_tg_user(1, tg_users[0], test=True)
        vpn_records = OutlineVPNKeys.objects.all()
        self.assertEqual(1, len(vpn_records))
        self.assertEqual(tg_users[0], vpn_records[0].telegram_user_record)


class GetAllVPNKeysOfUserTestCase(TestCase):
    def test_get_all_vpn_keys_of_user(self):
        tg_users = helpers.create_telegram_users(4)
        for cnt in range(len(tg_users) - 2):
            OutlineVPNKeys(
                telegram_user_record=tg_users[0],
                outline_key_id=cnt,
            ).save()
        key = OutlineVPNKeys.objects.get(outline_key_id=0)
        key.outline_key_valid_until = datetime.datetime.today() + datetime.timedelta(days=40)
        key.save()
        user_keys = processes.get_all_vpn_keys_of_user(tg_users[0].telegram_id)
        self.assertEqual(2, len(user_keys))


class ChangeVPNKeyIsActiveTestCase(TestCase):
    def test_change_vpn_key_is_active(self):
        vpn_key = helpers.create_vpn_keys()[0]
        self.assertFalse(vpn_key.outline_key_active)
        processes.change_vpn_key_is_active(vpn_key, test=True)
        self.assertTrue(vpn_key.outline_key_active)
        processes.change_vpn_key_is_active(vpn_key, test=True)
        self.assertFalse(vpn_key.outline_key_active)


class ChaneVPNValidUntilTestCase(TestCase):
    def test_change_vpn_key_valid_until(self):
        vpn_key = helpers.create_vpn_keys()[0]
        self.assertIsNotNone(vpn_key.outline_key_valid_until)
        processes.change_vpn_key_valid_until(vpn_key, 0)
        self.assertIsNone(vpn_key.outline_key_valid_until)
        processes.change_vpn_key_valid_until(vpn_key, 1)
        self.assertIsNotNone(vpn_key.outline_key_valid_until)
        self.assertIsInstance(vpn_key.outline_key_valid_until, datetime.date)

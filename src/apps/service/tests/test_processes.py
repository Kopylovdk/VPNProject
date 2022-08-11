from django.test import TestCase
from apps.service import exceptions
from apps.service.models import TelegramUsers
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

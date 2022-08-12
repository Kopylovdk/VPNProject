from django.test import TestCase
import apps.service.bot.bot_processes as bot_processes


class ValidateINTTestCase(TestCase):
    def setUp(self) -> None:
        self.int = '1'
        self.str = 'str'

    def test_validate_int_true(self):
        self.assertTrue(bot_processes.validate_int(self.int))

    def test_validate_int_false(self):
        self.assertFalse(bot_processes.validate_int(self.str))

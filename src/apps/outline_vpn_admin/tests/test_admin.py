from apps.outline_vpn_admin.admin import format_bytes_to_human
from django.test import TestCase


class FormatBytesToHumanTestCase(TestCase):
    def test_format_bytes_to_human(self):
        tests = [
            1,
            1024,
            500000,
            1048576,
            50000000,
            1073741824,
            5000000000,
            1099511627776,
            5000000000000,
            5000000000000500,
            5000000000000000009,
            5000000000000000009000,
            5000000000000000009000000,
        ]
        result = [
            '1.00 байт',
            '1.00 Кб',
            '488.28 Кб',
            '1.00 Мб',
            '47.68 Мб',
            '1.00 Гб',
            '4.66 Гб',
            '1.00 Тб',
            '4.55 Тб',
            '4.44 Пб',
            '4.34 Эб',
            '4.24 Зб',
            '4.14 Йб',
        ]
        for i, j in enumerate(tests):
            self.assertEqual(result[i], format_bytes_to_human(j))

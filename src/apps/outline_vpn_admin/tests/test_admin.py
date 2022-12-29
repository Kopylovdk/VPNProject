from apps.outline_vpn_admin.admin import format_bytes_to_human
from django.test import TestCase


class FormatBytesToHumanTestCase(TestCase):
    def test_format_bytes_to_human(self):
        tests = {
            0: '0 байт',
            1: '1.00 байт',
            1024: '1.00 Кб',
            500000: '488.28 Кб',
            1048576: '1.00 Мб',
            50000000: '47.68 Мб',
            1073741824: '1.00 Гб',
            5000000000: '4.66 Гб',
            1099511627776: '1.00 Тб',
            5000000000000: '4.55 Тб',
            5000000000000500: '4.44 Пб',
            5000000000000000009: '4.34 Эб',
            5000000000000000009000: '4.24 Зб',
            5000000000000000009000000: '4.14 Йб',
        }

        for bytes_, result in tests.items():
            self.assertEqual(
                result,
                format_bytes_to_human(bytes_)
            )

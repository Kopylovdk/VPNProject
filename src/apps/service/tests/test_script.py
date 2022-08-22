import datetime
import apps.service.tests.helpers as helpers
from django.test import TestCase
from apps.service.models import OutlineVPNKeys
from apps.service.script_vpnkeys_expired import collect_expired_vpn_keys, expire_vpn_key


class ScriptVPNKeysExpiredTestCase(TestCase):
    def setUp(self) -> None:
        self.date_today = datetime.datetime.today()
        self.vpn_keys = helpers.create_vpn_keys(cnt=6)
        for vpn_key in self.vpn_keys:
            if vpn_key.outline_key_id == 1:
                vpn_key.outline_key_valid_until = None
                vpn_key.outline_key_active = True
            elif vpn_key.outline_key_id in [2, 3]:
                date = self.date_today - datetime.timedelta(days=1)
                vpn_key.outline_key_valid_until = date
                vpn_key.outline_key_active = True
            elif vpn_key.outline_key_id == 4:
                vpn_key.outline_key_active = True
            elif vpn_key.outline_key_id == 5:
                vpn_key.outline_key_valid_until = self.date_today
                vpn_key.outline_key_active = True
            vpn_key.save()
        self.expired_keys_id = [2, 3]

    def test_collect_expired_vpn_keys(self):
        select_from_db = collect_expired_vpn_keys()
        self.assertEqual(2, len(select_from_db))

    def test_expire_vpn_key(self):
        for vpn_key in self.vpn_keys:
            key_id = vpn_key.outline_key_id
            if key_id in [1, 2, 3, 4, 5]:
                self.assertTrue(vpn_key.outline_key_active)
                if key_id == 1:
                    self.assertIsNone(vpn_key.outline_key_valid_until)
                else:
                    self.assertIsNotNone(vpn_key.outline_key_valid_until)
                    self.assertIsInstance(vpn_key.outline_key_valid_until, datetime.datetime)
            else:
                self.assertFalse(vpn_key.outline_key_active)

        expire_vpn_key(test=True)

        vpn_keys = OutlineVPNKeys.objects.all()
        for vpn_key in vpn_keys:
            if vpn_key.outline_key_id in self.expired_keys_id:
                self.assertFalse(vpn_key.outline_key_active)
                self.assertEqual(vpn_key.outline_key_traffic_limit, 1024)


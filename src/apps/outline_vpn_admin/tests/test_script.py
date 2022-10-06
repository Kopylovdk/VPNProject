import datetime
import apps.outline_vpn_admin.tests.helpers as helpers
from unittest.mock import patch
from django.test import TestCase
from apps.outline_vpn_admin.models import OutlineVPNKeys
from apps.outline_vpn_admin.scripts_vpnkeys import (
    collect_expired_vpn_keys,
    expire_vpn_key,
    collect_expired_soon_vpn_keys,
)
from apps.outline_vpn_admin.tests.test_processes import MockResponseStatusCode204


class MockResponseSendMessage:
    def __init__(self):
        self.status_code = 200


class BaseSetUp(TestCase):
    def setUp(self) -> None:
        self.date_today = datetime.datetime.now()
        self.user = helpers.create_telegram_users()[0]
        self.vpn_keys = helpers.create_vpn_keys(cnt=6)
        for vpn_key in self.vpn_keys:
            if vpn_key.outline_key_id == 1000:
                vpn_key.outline_key_valid_until = None
                vpn_key.outline_key_active = True
            elif vpn_key.outline_key_id in [1001, 1002]:
                date = self.date_today - datetime.timedelta(days=1)
                vpn_key.outline_key_valid_until = date
                vpn_key.outline_key_active = True
            elif vpn_key.outline_key_id == 1003:
                vpn_key.outline_key_valid_until = self.date_today + datetime.timedelta(days=7)
                vpn_key.outline_key_active = True
            elif vpn_key.outline_key_id == 1004:
                vpn_key.outline_key_valid_until = self.date_today
                vpn_key.outline_key_active = True
            vpn_key.telegram_user_record = self.user
            vpn_key.save()
        self.expired_keys_id = [1001, 1002]


class ScriptVPNKeysExpiredTestCase(BaseSetUp):

    def test_collect_expired_vpn_keys(self):
        select_from_db = collect_expired_vpn_keys()
        self.assertEqual(2, len(select_from_db))

    # TODO: Mock для бота
    @patch("requests.put", return_value=MockResponseStatusCode204())
    @patch('urllib3.connectionpool', return_value=MockResponseSendMessage())
    def test_expire_vpn_key(self, mock, mock_2):
        # print(self.vpn_keys[0].outline_key_id,
        #       self.vpn_keys[1].outline_key_id,
        #       self.vpn_keys[2].outline_key_id,
        #       self.vpn_keys[3].outline_key_id,
        #       self.vpn_keys[4].outline_key_id,
        #       self.vpn_keys[5].outline_key_id,
        #       )
        for vpn_key in self.vpn_keys:
            key_id = vpn_key.outline_key_id
            if key_id in [1000, 1001, 1002, 1003, 1004]:
                self.assertTrue(vpn_key.outline_key_active)
                if key_id == 1000:
                    self.assertIsNone(vpn_key.outline_key_valid_until)
                else:
                    self.assertIsNotNone(vpn_key.outline_key_valid_until)
                    self.assertIsInstance(vpn_key.outline_key_valid_until, datetime.datetime)
            else:
                # print(key_id)
                self.assertFalse(vpn_key.outline_key_active)

        expire_vpn_key()

        vpn_keys = OutlineVPNKeys.objects.all()
        for vpn_key in vpn_keys:
            if vpn_key.outline_key_id in self.expired_keys_id:
                self.assertFalse(vpn_key.outline_key_active)
                self.assertEqual(vpn_key.outline_key_traffic_limit, 1024)


class ScriptVPNKeysExpiredSoonTestCase(BaseSetUp):

    def test_collect_expired_soon_vpn_keys(self):
        days_before_expire = 7
        select_from_db = collect_expired_soon_vpn_keys(days_before_expire)
        self.assertEqual(1, len(select_from_db))
        expected_date = self.date_today + datetime.timedelta(days=days_before_expire)
        self.assertEqual(
            select_from_db[0].outline_key_valid_until.strftime("%d-%m-%Y"),
            expected_date.strftime("%d-%m-%Y")
        )


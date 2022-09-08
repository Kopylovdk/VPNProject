from django.test import TestCase
from apps.outline_vpn_admin.outline_api import get_outline_client
from outline_vpn.outline_vpn import OutlineVPN


class GetOutlineServerResponseTestCase(TestCase):
    def setUp(self) -> None:
        self.kz_server_name = "kz"
        self.kz_server_info = {
            'name': 'KZ',
            'serverId': 'c3b284b6-02b2-47da-b713-0bdfaa285a0c',
            'metricsEnabled': False,
            'createdTimestampMs': 1655721222656,
            'version': '1.6.1',
            'portForNewAccessKeys': 29876,
            'hostnameForAccessKeys': '194.110.55.249',
        }

    def test_get_outline_client_and_server_response_kz(self):
        client = get_outline_client(self.kz_server_name)
        self.assertIsInstance(client, OutlineVPN)
        self.assertEqual(client.get_server_information()['name'], 'KZ')
        self.assertEqual(client.get_server_information(), self.kz_server_info)

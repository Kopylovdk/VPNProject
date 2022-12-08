from django.test import TestCase
from apps.outline_vpn_admin import exceptions
from apps.outline_vpn_admin.outline_api import get_outline_client
from outline_vpn.outline_vpn import OutlineVPN
from apps.outline_vpn_admin.tests import helpers


class GetOutlineServerResponseTestCase(TestCase):
    def setUp(self) -> None:
        self.servers = helpers.create_vpn_server(2)
        self.servers[0].is_default = True
        self.servers[0].save()
        self.server_name = 'test_test_test'
        self.servers[1].name = self.server_name
        self.servers[1].save()
        self.server_error_name = 'test_test'

    def test_get_outline_client_default(self):
        client = get_outline_client()
        self.assertIsInstance(client, OutlineVPN)

    def test_get_outline_client_by_name(self):
        client = get_outline_client(vpn_server=self.servers[0])
        self.assertIsInstance(client, OutlineVPN)

    def test_get_outline_client_server_does_not_response(self):
        pass

import apps.outline_vpn_admin.tests.mocks as mocks
from django.test import TestCase
from apps.outline_vpn_admin import exceptions
from apps.outline_vpn_admin.outline_api import get_outline_client
from outline_vpn.outline_vpn import OutlineVPN
from apps.outline_vpn_admin.tests import helpers
from unittest.mock import patch


class GetOutlineServerResponseTestCase(TestCase):
    def setUp(self) -> None:
        self.server_1 = helpers.create_vpn_server()[0]
        self.server_1.is_default = True
        self.server_1.save()

        self.server_2_name = 'test_test_test'
        self.server_2 = helpers.create_vpn_server(server_name=self.server_2_name)[0]

        self.server_error_name = 'test_test'

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_get_outline_client_default(self, *args):
        client = get_outline_client()
        self.assertIsInstance(client, OutlineVPN)

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_get_outline_client_by_name(self, *args):
        client = get_outline_client(vpn_server=self.server_1)
        self.assertIsInstance(client, OutlineVPN)

    def test_get_outline_client_server_does_not_response(self):
        with self.assertRaises(exceptions.VPNServerDoesNotResponse) as err:
            get_outline_client(vpn_server=self.server_1)
        self.assertIn(self.server_1.name, str(err.exception.message))

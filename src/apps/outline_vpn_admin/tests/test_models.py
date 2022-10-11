from decimal import Decimal

from django.test import TestCase
from apps.outline_vpn_admin.tests import helpers
from apps.outline_vpn_admin.models import (
    Client,
    Contact,
    Transport,
    VPNToken,
    VPNServer,
    Tariffication,
)


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        self.cnt = 100
        self.test_str_value = 'test'


class ClientTestCase(BaseTestCase):
    def test_create_clients(self):
        self.assertEqual(self.cnt, len(helpers.create_client(self.cnt)))
        self.assertEqual(self.cnt, len(Client.objects.all()))
        obj = Client.objects.first()
        self.assertIn(self.test_str_value, obj.full_name)
        self.assertIsNotNone(obj.created_at)
        self.assertIsNotNone(obj.updated_at)


class TransportTestCase(BaseTestCase):
    def test_create_transports(self):
        self.assertEqual(self.cnt, len(helpers.create_transport(self.cnt)))
        self.assertEqual(self.cnt, len(Transport.objects.all()))
        obj = Transport.objects.first()
        self.assertIn(self.test_str_value, obj.name)
        self.assertEqual(helpers.TRANSPORT_CREDENTIALS, obj.credentials)
        self.assertIsNotNone(obj.created_at)
        self.assertIsNotNone(obj.updated_at)


class ContactTestCase(BaseTestCase):
    def test_create_contacts(self):
        self.assertEqual(self.cnt, len(helpers.create_contact(self.cnt)))
        self.assertEqual(self.cnt, len(Contact.objects.all()))
        obj = Contact.objects.first()
        self.assertIsInstance(obj.client, Client)
        self.assertIsInstance(obj.transport, Transport)
        self.assertIn(self.test_str_value, obj.name)
        self.assertEqual(helpers.CONTACT_CREDENTIALS, obj.credentials)
        self.assertIsNotNone(obj.created_at)
        self.assertIsNotNone(obj.updated_at)


class VPNTokenTestCase(BaseTestCase):
    def test_create_vpn_tokens(self):
        self.assertEqual(self.cnt, len(helpers.create_vpn_token(self.cnt)))
        self.assertEqual(self.cnt, len(VPNToken.objects.all()))
        obj = VPNToken.objects.first()
        self.assertIn(self.test_str_value, obj.name)
        self.assertIn(self.test_str_value, obj.vpn_key)
        self.assertIsInstance(obj.client, Client)
        self.assertIsInstance(obj.server, VPNServer)
        self.assertIsInstance(obj.outline_id, int)
        self.assertIsNone(obj.traffic_limit)
        self.assertIsNone(obj.valid_until)
        self.assertTrue(obj.is_active)
        self.assertIsNotNone(obj.created_at)
        self.assertIsNotNone(obj.updated_at)


class VPNServerTestCase(BaseTestCase):
    def test_create_vpn_server(self):
        self.assertEqual(self.cnt, len(helpers.create_vpn_server(self.cnt)))
        self.assertEqual(self.cnt, len(VPNServer.objects.all()))
        obj = VPNServer.objects.first()
        self.assertIn(self.test_str_value, obj.name)
        self.assertIn(self.test_str_value, obj.uri)
        self.assertIsNotNone(obj.created_at)
        self.assertIsNotNone(obj.updated_at)


class TarifficationTestCase(BaseTestCase):
    def test_create_tariffications(self):
        self.assertEqual(self.cnt, len(helpers.create_tariffication(self.cnt)))
        self.assertEqual(self.cnt, len(Tariffication.objects.all()))
        obj = Tariffication.objects.first()
        self.assertIn(self.test_str_value, obj.name)
        self.assertTrue(obj.is_active)
        self.assertIsInstance(obj.prolong_days, int)
        self.assertIsInstance(obj.price, Decimal)
        self.assertIsNotNone(obj.valid_until)
        self.assertIsNotNone(obj.created_at)
        self.assertIsNotNone(obj.updated_at)

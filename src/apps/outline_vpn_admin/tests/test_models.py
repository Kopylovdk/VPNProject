from decimal import Decimal
from django.test import TestCase
from apps.outline_vpn_admin.tests import helpers
from apps.outline_vpn_admin.models import (
    Client,
    Contact,
    Transport,
    VPNToken,
    VPNServer,
    Tariff,
)


class BaseTestCase(TestCase):
    def setUp(self) -> None:
        self.cnt = 100
        self.test_str_value = 'test'
        self.cred = {'id': 9999, 'first_name': 'fill_details', 'last_name': 'fill_details'}
        self.name = 'test_make'


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
        transport = Transport.objects.first()
        self.assertIn(self.test_str_value, transport.name)
        self.assertEqual(helpers.TRANSPORT_CREDENTIALS, transport.credentials)
        self.assertIsNotNone(transport.created_at)
        self.assertIsNotNone(transport.updated_at)

    def test_make_contact_credentials_uid(self):
        transport = helpers.create_transport()[0]
        transport.name = self.name
        transport.save()
        self.assertEqual(transport.make_contact_credentials_uid(self.cred), f'{self.name}@{self.cred["id"]}')

    def test_fill_client_details(self):
        client = helpers.create_client()[0]
        transport = helpers.create_transport()[0]
        self.assertEqual(
            transport.fill_client_details(client, self.cred).full_name,
            f'{self.cred["first_name"]} {self.cred["last_name"]}'
        )


class ContactTestCase(BaseTestCase):
    def test_create_contacts(self):
        self.assertEqual(
            self.cnt,
            len(helpers.create_contact(
                cnt=self.cnt,
                client=helpers.create_client()[0],
                transport=helpers.create_transport()[0]
                )
            )
        )
        self.assertEqual(self.cnt, len(Contact.objects.all()))
        contact = Contact.objects.first()
        self.assertIsInstance(contact.client, Client)
        self.assertIsInstance(contact.transport, Transport)
        self.assertEqual(helpers.CONTACT_CREDENTIALS, contact.credentials)
        self.assertIsNotNone(contact.created_at)
        self.assertIsNotNone(contact.updated_at)


class VPNTokenTestCase(BaseTestCase):
    def test_create_vpn_tokens(self):
        self.assertEqual(
            self.cnt,
            len(helpers.create_vpn_token(
                cnt=self.cnt,
                vpn_server=helpers.create_vpn_server()[0],
                client=helpers.create_client()[0],
                )
            )
        )
        self.assertEqual(self.cnt, len(VPNToken.objects.all()))
        token = VPNToken.objects.first()
        self.assertIn(self.test_str_value, token.name)
        self.assertIn(self.test_str_value, token.vpn_key)
        self.assertIsInstance(token.client, Client)
        self.assertIsInstance(token.server, VPNServer)
        self.assertIsInstance(token.outline_id, int)
        self.assertIsNone(token.traffic_limit)
        self.assertIsNone(token.valid_until)
        self.assertTrue(token.is_active)
        self.assertIsNotNone(token.created_at)
        self.assertIsNotNone(token.updated_at)


class VPNServerTestCase(BaseTestCase):
    def test_create_vpn_server(self):
        self.assertEqual(self.cnt, len(helpers.create_vpn_server(self.cnt)))
        self.assertEqual(self.cnt, len(VPNServer.objects.all()))
        obj = VPNServer.objects.first()
        self.assertIn(self.test_str_value, obj.name)
        self.assertIn(self.test_str_value, obj.uri)
        self.assertFalse(obj.is_default)
        self.assertIsNotNone(obj.created_at)
        self.assertIsNotNone(obj.updated_at)


class TarifficationTestCase(BaseTestCase):
    def test_create_tariffications(self):
        self.assertEqual(self.cnt, len(helpers.create_tariff(self.cnt)))
        self.assertEqual(self.cnt, len(Tariff.objects.all()))
        tariff = Tariff.objects.first()
        self.assertIn(self.test_str_value, tariff.name)
        self.assertTrue(tariff.is_active)
        self.assertIsInstance(tariff.prolong_period, int)
        self.assertIsInstance(tariff.price, Decimal)
        self.assertIsNotNone(tariff.valid_until)
        self.assertIsNotNone(tariff.created_at)
        self.assertIsNotNone(tariff.updated_at)

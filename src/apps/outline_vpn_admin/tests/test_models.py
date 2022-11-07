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
    Currency,
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
        self.assertEqual(self.cnt, Client.objects.all().count())
        client = Client.objects.first()
        self.assertIn(self.test_str_value, client.full_name)
        self.assertIsNotNone(client.created_at)
        self.assertIsNotNone(client.updated_at)

    def test_is_has_demo_false(self):
        client = helpers.create_client()[0]
        self.assertFalse(client.is_has_demo())
        token = helpers.create_vpn_token(
            client=client,
            vpn_server=helpers.create_vpn_server()[0],
            tariff=helpers.create_tariff(
                currency=helpers.create_currency()[0]
            )[0]
        )[0]
        token.is_demo = True
        token.save()
        self.assertTrue(client.is_has_demo())

    def test_is_token_owner(self):
        client = helpers.create_client()[0]
        self.assertFalse(client.is_token_owner(999))
        token = helpers.create_vpn_token(
            client=client,
            vpn_server=helpers.create_vpn_server()[0],
            tariff=helpers.create_tariff(
                currency=helpers.create_currency()[0]
            )[0]
        )[0]
        token.outline_id = 999
        token.save()
        self.assertTrue(client.is_token_owner(999))


class TransportTestCase(BaseTestCase):
    def test_create_transports(self):
        exist = Transport.objects.all().count()
        self.assertEqual(self.cnt, len(helpers.create_transport(self.cnt)))
        self.assertEqual(self.cnt, Transport.objects.all().count() - exist)
        transport = Transport.objects.last()
        self.assertIn(self.test_str_value, transport.name)
        self.assertEqual(helpers.TRANSPORT_CREDENTIALS, transport.credentials)
        self.assertIsNotNone(transport.created_at)
        self.assertIsNotNone(transport.updated_at)

    def test_make_contact_credentials_uid(self):
        transport = helpers.create_transport()[0]
        transport.name = self.name
        transport.save()
        self.assertEqual(transport.make_contact_credentials_uid(self.cred), f'{self.name}@{self.cred["id"]}')

    def test_make_contact_messenger_id_uid(self):
        transport = helpers.create_transport()[0]
        transport.name = self.name
        transport.save()
        self.assertEqual(transport.make_contact_messenger_id_uid(self.cred["id"]), f'{self.name}@{self.cred["id"]}')

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
        self.assertEqual(self.cnt, Contact.objects.all().count())
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
                tariff=helpers.create_tariff(
                    currency=helpers.create_currency()[0]
                )[0]
            )
            )
        )
        self.assertEqual(self.cnt, VPNToken.objects.all().count())
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
        exist = VPNServer.objects.all().count()
        self.assertEqual(self.cnt, len(helpers.create_vpn_server(self.cnt)))
        self.assertEqual(self.cnt, VPNServer.objects.all().count() - exist)
        obj = VPNServer.objects.last()
        self.assertIn(self.test_str_value, obj.name)
        self.assertIn(self.test_str_value, obj.uri)
        self.assertFalse(obj.is_default)
        self.assertIsNotNone(obj.created_at)
        self.assertIsNotNone(obj.updated_at)


class TarifficationTestCase(BaseTestCase):
    def test_create_tariffications(self):
        exist = Tariff.objects.all().count()
        self.assertEqual(
            self.cnt,
            len(helpers.create_tariff(
                currency=helpers.create_currency()[0],
                cnt=self.cnt
            )
            )
        )
        self.assertEqual(self.cnt, Tariff.objects.all().count() - exist)
        tariff = Tariff.objects.last()
        self.assertIn(self.test_str_value, tariff.name)
        self.assertTrue(tariff.is_active)
        self.assertIsInstance(tariff.prolong_period, int)
        self.assertIsInstance(tariff.price, Decimal)
        self.assertIsNotNone(tariff.valid_until)
        self.assertIsNotNone(tariff.created_at)
        self.assertIsNotNone(tariff.updated_at)


class CurrencyTestCase(BaseTestCase):
    def test_create_currencies(self):
        self.assertEqual(3, len(helpers.create_currency()))
        obj = Currency.objects.first()
        self.assertTrue(obj.is_main)
        self.assertIsNotNone(obj.created_at)
        self.assertIsNotNone(obj.updated_at)

import apps.outline_vpn_admin.processes as processes
import apps.outline_vpn_admin.tests.helpers as helpers
from copy import copy
from unittest.mock import patch
from django.test import TestCase
from apps.outline_vpn_admin import exceptions
from apps.outline_vpn_admin.models import (
    Contact,
    VPNToken,
    Tariff,
    Transport,
    VPNServer
)
from apps.outline_vpn_admin.tests.mocks import (
    MockResponseCreateKey,
    MockResponseStatusCode204,
)
from vpnservice.settings import DATE_STRING_FORMAT


# TODO: Доделать тесты, передалать все тесты в божеский вид

class GetTransportContact(TestCase):
    def setUp(self) -> None:
        self.transport_name = 'test_test_test'
        self.cred = {'id': 9999999, "first_name": "some", "phone_number": '', "last_name": "some"}

    def test_get_transport_contact_by_credentials(self):
        transports = helpers.create_transport(transport_name=self.transport_name)
        clients = helpers.create_client()
        contacts = helpers.create_contact(
            transport=transports[0],
            client=clients[0],
            credentials=self.cred
        )
        transport, contact = processes.get_transport_contact_by_(
            transport_name=self.transport_name,
            credentials=self.cred
        )
        self.assertIsInstance(transport, Transport)
        self.assertIsInstance(contact, Contact)
        self.assertEqual(contact.transport, transports[0])
        self.assertEqual(contact.client, clients[0])
        self.assertEqual(contact, contacts[0])
        self.assertEqual(transport, transports[0])
        self.assertEqual(transport.name, self.transport_name)
        self.assertEqual(contact.credentials, self.cred)

    def test_get_transport_contact_by_messenger_id(self):
        transports = helpers.create_transport(transport_name=self.transport_name)
        clients = helpers.create_client()
        contacts = helpers.create_contact(
            transport=transports[0],
            client=clients[0],
            credentials=self.cred
        )
        transport, contact = processes.get_transport_contact_by_(
            transport_name=self.transport_name,
            messenger_id=self.cred['id']
        )

        self.assertIsInstance(transport, Transport)
        self.assertIsInstance(contact, Contact)
        self.assertEqual(contact.transport, transports[0])
        self.assertEqual(contact.client, clients[0])
        self.assertEqual(contact, contacts[0])
        self.assertEqual(transport, transports[0])
        self.assertEqual(transport.name, self.transport_name)
        self.assertEqual(contact.credentials, self.cred)

    def test_get_transport_contact_by_transport_does_not_exist(self):
        with self.assertRaises(exceptions.TransportDoesNotExist) as err:
            processes.get_transport_contact_by_(transport_name=self.transport_name, credentials=self.cred)
        self.assertIn(f'Bot {self.transport_name!r} does not exist', err.exception.message)

    def test_get_transport_contact_by_user_does_not_exist(self):
        helpers.create_transport(transport_name=self.transport_name)
        with self.assertRaises(exceptions.UserDoesNotExist) as err:
            processes.get_transport_contact_by_(transport_name=self.transport_name, credentials=self.cred)
        self.assertIn(f'User does not exist', err.exception.message)


class CreateOrUpdateContactTestCase(TestCase):
    clients = None
    data = None
    contacts = None
    transports = None

    @classmethod
    def setUpTestData(cls) -> None:
        cls.data = {"id": 9999, "first_name": "some", "last_name": "some", "phone_number": ''}
        cls.clients = helpers.create_client(3)
        cls.transports = helpers.create_transport(2)
        cls.transports[0].name = 'telegram'
        cls.transports[0].save()
        helpers.create_contact(
            client=cls.clients[0],
            transport=cls.transports[1],
            cnt=3
        )
        helpers.create_contact(
            client=cls.clients[1],
            transport=cls.transports[0],
            credentials=cls.data,
        )
        helpers.create_contact(
            client=cls.clients[2],
            transport=cls.transports[1]
        )
        cls.contacts = Contact.objects.all()

        cls.send_json = {
            "transport_name": "telegram",
            "credentials": {
                "id": 9999,
                "first_name": "first_name",
                "last_name": "last_name",
                "login": "login",
                "phone_number": 1234567890,
            }
        }

    def test_create_or_update_client_contact_create(self):
        to_send = copy(self.send_json)
        to_send["credentials"]["id"] = 222
        uid_check = self.transports[0].make_contact_credentials_uid(to_send["credentials"])
        contacts = self.transports[0].contact_set
        self.assertFalse(contacts.filter(uid=uid_check))

        response = processes.create_or_update_contact(transport_name=to_send['transport_name'],
                                                      credentials=to_send["credentials"])

        created_contact = Contact.objects.select_related('client', 'transport').last()

        self.assertIn('details', response.keys())
        self.assertEqual('Created new user', response['details'])
        self.assertEqual(response['user_info']['contact']["credentials"], to_send["credentials"])

        self.assertEqual(response['user_info']['user'], created_contact.client.as_dict())
        self.assertEqual(
            response['user_info']['user']['full_name'],
            f'{to_send["credentials"]["first_name"]} {to_send["credentials"]["last_name"]}'
        )
        new_uid = self.transports[0].make_contact_credentials_uid(to_send["credentials"])
        self.assertEqual(new_uid, created_contact.uid)

        self.assertEqual(created_contact.transport, self.transports[0])
        self.assertEqual(created_contact.transport.name, self.transports[0].name)

    def test_create_or_update_client_contact_update(self):
        cred_before = Contact.objects.get(credentials__id=self.send_json["credentials"]["id"]).credentials
        self.assertEqual(cred_before, self.data)

        response = processes.create_or_update_contact(transport_name=self.send_json['transport_name'],
                                                      credentials=self.send_json["credentials"])

        self.assertIn('details', response.keys())
        self.assertEqual('Updated exist user', response['details'])

        cred_after = Contact.objects.get(credentials__id=self.send_json["credentials"]["id"]).credentials

        self.assertEqual(cred_after, self.send_json["credentials"])
        self.assertNotEqual(cred_before, cred_after)


class GetClientTokens(TestCase):
    tariff = None
    cred_no_token = None
    token_1 = None
    token_2 = None
    token_3 = None
    vpn_servers = None
    contact_first = None
    cred = None
    clients = None
    transports = None

    @classmethod
    def setUpTestData(cls) -> None:
        cls.clients = helpers.create_client(3)
        cls.transports = helpers.create_transport(2)
        cls.transports[0].name = 'telegram'
        cls.transports[0].save()
        cls.tariff = helpers.create_tariff(currency=helpers.create_currency()[0])[0]
        cls.vpn_servers = helpers.create_vpn_server()
        cls.cred = {
            "id": 1000,
            "first_name": "first_name",
            "last_name": "last_name",
            "login": "login",
            "phone_number": '',
        }
        cls.contact_first = helpers.create_contact(cls.clients[0], cls.transports[0], cls.cred)[0]
        helpers.create_contact(cls.clients[1], cls.transports[1])

        cls.cred_no_token = {
            "id": 1001,
            "first_name": "first_name",
            "last_name": "last_name",
            "login": "login",
            "phone_number": '',
        }
        helpers.create_contact(cls.clients[2], cls.transports[0], cls.cred_no_token)

        cls.token_1 = helpers.create_vpn_token(cls.clients[0], cls.vpn_servers[0], cls.tariff)[0]
        cls.token_1.outline_id = 1
        cls.token_1.save()
        cls.token_2 = helpers.create_vpn_token(cls.clients[0], cls.vpn_servers[0], cls.tariff)[0]
        cls.token_2.outline_id = 2
        cls.token_2.save()
        cls.token_3 = helpers.create_vpn_token(cls.clients[1], cls.vpn_servers[0], cls.tariff)[0]
        cls.token_3.outline_id = 3
        cls.token_3.save()

    def test_get_client_tokens(self):

        response = processes.get_client_tokens(
            transport_name=self.transports[0].name,
            messenger_id=self.cred['id']
        )

        self.assertIn('details', response.keys())
        self.assertIn('client_tokens', response['details'])
        self.assertEqual(2, len(response['tokens']))
        self.assertIn('user_info', response.keys())
        self.assertIn('user', response['user_info'].keys())
        self.assertIn('credentials', response['user_info']['contact'].keys())

        self.assertEqual(response['user_info']['contact']['credentials'], self.cred)
        self.assertEqual(response['user_info']['user']['id'], self.contact_first.client.id)
        self.assertEqual(response['user_info']['user']['full_name'], self.contact_first.client.full_name)

    def test_get_client_tokens_no_tokens(self):
        response = processes.get_client_tokens(
            transport_name=self.transports[0].name,
            messenger_id=self.cred_no_token['id']
        )
        self.assertEqual(0, len(response['tokens']))
        self.assertIsInstance(response['tokens'], list)


class TokenBaseTestCase(TestCase):
    token = None
    tariffs = None
    vpn_server = None
    contact_first = None
    cred = None
    clients = None
    transport = None

    @classmethod
    def setUpTestData(cls) -> None:
        cls.clients = helpers.create_client(2)
        cls.transport = helpers.create_transport()[0]
        cls.transport.name = 'telegram'
        cls.transport.save()
        cls.tariffs = helpers.create_tariff(
            currency=helpers.create_currency()[0],
            cnt=3
        )
        cls.vpn_server = helpers.create_vpn_server()[0]
        cls.vpn_server.name = 'kz'
        cls.vpn_server.save()
        cls.cred = {
            "id": 1000,
            "first_name": "first_name",
            "last_name": "last_name",
            "login": "login",
            "phone_number": '',
        }
        cls.contact_first = helpers.create_contact(cls.clients[0], cls.transport, cls.cred)[0]

        cls.token = helpers.create_vpn_token(
            client=cls.clients[0],
            vpn_server=cls.vpn_server,
            tariff=cls.tariffs[0]
        )[0]
        cls.token.outline_id = 9000
        cls.token.save()


class TokenNewTestCase(TokenBaseTestCase):
    @patch("requests.put", return_value=MockResponseStatusCode204())
    @patch("requests.post", return_value=MockResponseCreateKey())
    def test_token_new(self, mocked_put, mocked_post):
        response = processes.token_new(
            transport_name="telegram",
            server_name="kz",
            credentials={"id": 1000, "some": "data", "phone_number": ''},
            tariff_name=self.tariffs[0].name,
        )
        self.assertEqual(response['details'], 'new_token by client')
        self.assertEqual(response['tokens'][0]['outline_id'], 9999)
        new_token = VPNToken.objects.get(outline_id=9999)
        self.assertTrue(new_token.is_active)
        new_token_dict = new_token.as_dict()
        new_token_dict['valid_until'] = new_token_dict['valid_until'].strftime(DATE_STRING_FORMAT)
        self.assertEqual(response['tokens'][0], new_token_dict)
        self.assertEqual(self.clients[0].as_dict(), response['user_info']['user'])
        self.assertEqual(self.contact_first.as_dict(), response['user_info']['contact'])

    def test_token_new_admin_ok(self):
        pass

    def test_token_new_admin_demo_not_allowed(self):
        pass

    def test_token_new_vpn_server_does_not_exist(self):
        not_exist_vpn_server = "no_name"
        with self.assertRaises(exceptions.VPNServerDoesNotExist) as err:
            processes.token_new(
                transport_name="telegram",
                server_name=not_exist_vpn_server,
                credentials={"id": 1000, "some": "data", "phone_number": ''},
                tariff_name=self.tariffs[0].name,
            )
        self.assertEqual(
            f'VPN Server {not_exist_vpn_server!r} does not exist',
            str(err.exception.message)
        )

    def test_token_new_tariff_does_not_exist(self):
        not_exist_tariff = "no_name"
        with self.assertRaises(exceptions.TariffDoesNotExist) as err:
            processes.token_new(
                transport_name="telegram",
                server_name="kz",
                credentials={"id": 1000, "some": "data", "phone_number": ''},
                tariff_name=not_exist_tariff,
            )
        self.assertEqual(
            f'Tariff {not_exist_tariff!r} does not exist',
            str(err.exception.message)
        )

    def test_token_new_demo_key_exist(self):
        contact = helpers.create_contact(
            client=helpers.create_client()[0],
            transport=self.transport,
            credentials={"id": 909090, "some": "data", "phone_number": ''}
        )[0]
        token_demo = helpers.create_vpn_token(
            client=contact.client,
            vpn_server=self.vpn_server,
            tariff=self.tariffs[0],
        )[0]
        self.tariffs[0].is_demo = True
        self.tariffs[0].save()
        token_demo.is_demo = True
        token_demo.save()
        with self.assertRaises(exceptions.DemoKeyExist) as err:
            processes.token_new(
                transport_name="telegram",
                server_name='kz',
                credentials={"id": 909090, "some": "data", "phone_number": ''},
                tariff_name=self.tariffs[0].name
            )
        self.assertEqual(
            f'User already have demo key',
            str(err.exception.message)
        )


class TokenRenewTestCase(TokenBaseTestCase):
    @patch("requests.delete", return_value=MockResponseStatusCode204())
    @patch("requests.put", return_value=MockResponseStatusCode204())
    @patch("requests.post", return_value=MockResponseCreateKey())
    def test_token_renew_ok(self, mocked_put, mocked_post, mocked_delete):
        self.assertTrue(self.token.is_active)
        self.assertEqual(1, VPNToken.objects.all().count())
        response = processes.token_renew(
            transport_name="telegram",
            credentials={"id": 1000, "some": "data", "phone_number": ''},
            token_id=self.token.id,
        )

        self.token.refresh_from_db()

        self.assertEqual(2, VPNToken.objects.all().count())
        self.assertEqual(response['details'], 'renew_token by client')
        self.assertEqual(response['tokens'][0]['outline_id'], 9999)

        new_token = VPNToken.objects.get(outline_id=9999)
        self.assertTrue(new_token.is_active)
        self.assertFalse(self.token.is_active)
        self.assertIn('Renewed by client', self.token.name)
        self.assertEqual(response['tokens'][0], new_token.as_dict())
        self.assertEqual(self.clients[0].as_dict(), response['user_info']['user'])
        self.assertEqual(self.contact_first.as_dict(), response['user_info']['contact'])

    def test_token_renew_admin_ok(self):
        # TODO:
        pass

    def test_token_renew_belong_to_another_user(self):
        with self.assertRaises(exceptions.BelongToAnotherUser) as err:
            processes.token_renew(
                transport_name="telegram",
                credentials={"id": 1000, "some": "data", "phone_number": ''},
                token_id=959595,
            )
        self.assertEqual('Error token renew. Token belongs to another user.', str(err.exception.message))

    def test_token_renew_renew_demo_key_not_allowed(self):
        # TODO:
        pass


class GetTariffTestCase(TestCase):
    tariffications = None

    @classmethod
    def setUpTestData(cls):
        cls.tariffications = helpers.create_tariff(currency=helpers.create_currency()[0], cnt=6)
        cls.tariffications[5].is_active = False
        cls.tariffications[5].save()

    def test_get_tariffications(self):
        response = processes.get_tariff()
        self.assertEqual(len(response['tariffs']), Tariff.objects.filter(is_active=True).count())
        self.assertIn("get_tariff", response["details"])


class GetVPNServersTestCase(TestCase):
    def test_get_vpn_servers(self):
        helpers.create_vpn_server(5)
        response = processes.get_vpn_servers()
        self.assertEqual(len(response['vpn_servers']), VPNServer.objects.all().count())


class GetClientTestCase(TokenBaseTestCase):
    def test_get_client(self):
        response = processes.get_client(
            messenger_id=self.cred['id'],
            transport_name="telegram",
        )
        self.assertEqual(response['details'], "get_client")
        self.assertIn('user_info', response.keys())
        self.assertIn('user', response['user_info'].keys())
        self.assertIn('contact', response['user_info'].keys())


class GetTransportsTestCase(TestCase):
    def test_get_transports_ok(self):
        response = processes.get_transports()
        self.assertIn("get_bots", response['details'])
        self.assertEqual(2, len(response['bots']))


class GetTokenTestCase(TestCase):
    def test_get_token_ok(self):
        pass

    def test_get_token_does_not_exist(self):
        pass


class GetTokenInfoTestCase(TestCase):
    def test_get_token_info(self):
        pass


class AddTrafficLimitTestCase(TestCase):
    def test_add_traffic_limit_ok(self):
        pass

    def test_add_traffic_limit_vpn_server_response_error(self):
        pass


class DelTrafficLimitTestCase(TestCase):
    def test_del_traffic_limit_ok(self):
        pass

    def test_del_traffic_limit_vpn_server_response_error(self):
        pass


class DelOutlineVPNKeyTestCase(TestCase):
    def test_del_outline_vpn_key_ok(self):
        pass

    def test_del_outline_vpn_key_vpn_server_response_error(self):
        pass


class TelegramMessageSenderTestCase(TestCase):
    def test_telegram_message_sender_ok_personal(self):
        pass

    def test_telegram_message_sender_ok_all_users(self):
        pass

    def test_telegram_message_sender_transport_does_not_exist(self):
        pass

    def test_telegram_message_sender_personal_transport_message_send_error(self):
        pass


class TokenAdminNewTestCase(TestCase):
    def test_token_admin_new_ok(self):
        pass


class TokenAdminRenewTestCase(TestCase):
    def test_token_admin_renew_ok(self):
        pass

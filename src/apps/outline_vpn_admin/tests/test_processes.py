import datetime

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
    VPNServer, Client,
)
from apps.outline_vpn_admin.tests import mocks as mocks
from vpnservice.settings import DATE_STRING_FORMAT


class BaseSetUpConfig(TestCase):
    def setUp(self) -> None:
        self.contact_client = helpers.create_client()[0]
        self.transport_name = 'test'
        self.transport_cnt = Transport.objects.count()
        self.transport = helpers.create_transport(transport_name=self.transport_name)[0]
        self.valid_messenger_id = 9999999
        self.credentials = {'id': self.valid_messenger_id, 'phone_number': '9999', 'first_name': 'test', 'last_name': 'test'}
        self.invalid_messenger_id = 98989898
        self.not_exist_transport_name = 'not_exist'
        self.not_exist_server_name = self.not_exist_transport_name
        self.not_exist_tariff_name = self.not_exist_transport_name
        self.not_exist_cont_cred = {'id': self.invalid_messenger_id}
        self.contact = helpers.create_contact(
            client=self.contact_client,
            transport=self.transport,
            credentials=self.credentials
        )[0]
        self.tariffs = helpers.create_tariff(
            cnt=2,
            currency=helpers.create_currency()[0]
        )
        self.tariffs[0].is_demo = True
        self.tariffs[0].save()
        self.tariff_demo = self.tariffs[0]
        self.tariff = self.tariffs[1]
        self.server_name = 'test_server_name'
        self.new_contact_credentials = {
            "id": 98989891,
            "first_name": "new first_name",
            "last_name": "new last_name",
            "phone_number": '987654321'
        }
        self.vpn_server = helpers.create_vpn_server(server_name=self.server_name)[0]
        self.vpn_token_demo = helpers.create_vpn_token(
            client=self.contact_client,
            vpn_server=self.vpn_server,
            tariff=self.tariff_demo
        )[0]
        self.vpn_token_demo.is_demo = True
        self.vpn_token_demo.outline_id = 919191
        self.vpn_token_demo.save()
        self.vpn_token = helpers.create_vpn_token(
            client=self.contact_client,
            vpn_server=self.vpn_server,
            tariff=self.tariff
        )[0]
        self.vpn_tokens_cnt = 2
        self.details_key_name = 'details'
        self.invalid_token_id = 123123123
        self.traffic_limit_in_bytes = 1024 * 1024 * 1024


class GetTransportContactTestCase(BaseSetUpConfig):
    def test_get_transport_contact_by_credentials(self):
        transport, contact = processes.get_transport_contact_by_(
            transport_name=self.transport_name,
            credentials=self.credentials
        )
        self.assertIsInstance(transport, Transport)
        self.assertIsInstance(contact, Contact)
        self.assertEqual(contact.transport, self.transport)
        self.assertEqual(contact.client, self.contact_client)
        self.assertEqual(contact, self.contact)
        self.assertEqual(transport, self.transport)
        self.assertEqual(transport.name, self.transport_name)
        self.assertEqual(contact.credentials, self.credentials)

    def test_get_transport_contact_by_messenger_id(self):
        transport, contact = processes.get_transport_contact_by_(
            transport_name=self.transport_name,
            messenger_id=self.credentials['id']
        )
        self.assertIsInstance(transport, Transport)
        self.assertIsInstance(contact, Contact)
        self.assertEqual(contact.transport, self.transport)
        self.assertEqual(contact.client, self.contact_client)
        self.assertEqual(contact, self.contact)
        self.assertEqual(transport, self.transport)
        self.assertEqual(transport.name, self.transport_name)
        self.assertEqual(contact.credentials, self.credentials)

    def test_get_transport_contact_by_transport_does_not_exist(self):
        with self.assertRaises(exceptions.TransportDoesNotExist) as err:
            processes.get_transport_contact_by_(
                transport_name=self.not_exist_transport_name,
                credentials=self.credentials
            )
        self.assertIn(
            f'Transport {self.not_exist_transport_name!r} does not exist',
            err.exception.message
        )

    def test_get_transport_contact_by_user_does_not_exist(self):
        with self.assertRaises(exceptions.UserDoesNotExist) as err:
            processes.get_transport_contact_by_(
                transport_name=self.transport_name,
                credentials=self.not_exist_cont_cred
            )
        self.assertIn(f'User does not exist', err.exception.message)


class CreateOrUpdateContactTestCase(BaseSetUpConfig):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.details_new = 'Created new user'
        cls.details_update = 'Updated exist user'
        cls.data_key_name = 'user_info'

    def test_create_or_update_client_contact_create(self):
        uid_check = self.transport.make_contact_credentials_uid(self.new_contact_credentials)
        self.assertFalse(self.transport.contact_set.filter(uid=uid_check))
        response = processes.create_or_update_contact(
            transport_name=self.transport_name,
            credentials=self.new_contact_credentials,
        )
        self.assertIn(self.details_key_name, response.keys())
        self.assertEqual(self.details_new, response[self.details_key_name])
        user_info = response[self.data_key_name]
        self.assertEqual(user_info['contact']["credentials"], self.new_contact_credentials)
        self.assertEqual(
            user_info['user']['full_name'],
            f'{self.new_contact_credentials["first_name"]} {self.new_contact_credentials["last_name"]}'
        )
        created_contact = Contact.objects.select_related('client', 'transport').last()
        self.assertEqual(user_info['user'], created_contact.client.as_dict())
        self.assertEqual(uid_check, created_contact.uid)
        self.assertEqual(created_contact.transport, self.transport)
        self.assertEqual(created_contact.transport.name, self.transport.name)

    def test_create_or_update_client_contact_update(self):
        new_credentials = copy(self.credentials)
        new_credentials['first_name'] = 'updated'
        qnt_before = Contact.objects.count()
        response = processes.create_or_update_contact(
            transport_name=self.transport_name,
            credentials=new_credentials,
        )
        self.assertIn(self.details_key_name, response.keys())
        self.assertEqual(self.details_update, response[self.details_key_name])
        user_info = response[self.data_key_name]
        self.assertEqual(new_credentials, user_info['contact']['credentials'])
        self.assertNotEqual(self.credentials, new_credentials)
        qnt_after = Contact.objects.count()
        self.assertEqual(qnt_before, qnt_after)


class GetClientTokensTestCase(BaseSetUpConfig):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.details = 'client_tokens'
        cls.data_key_name = 'tokens'

    def test_get_client_tokens(self):
        response = processes.get_client_tokens(
            transport_name=self.transport_name,
            messenger_id=self.valid_messenger_id,
        )
        self.assertIn(self.details_key_name, response.keys())
        self.assertEqual(self.details, response[self.details_key_name])
        self.assertEqual(2, len(response[self.data_key_name]))

        self.assertIn('user_info', response.keys())
        self.assertIn('user', response['user_info'].keys())
        self.assertIn('credentials', response['user_info']['contact'].keys())
        self.assertEqual(response['user_info']['contact']['credentials'], self.credentials)
        self.assertEqual(response['user_info']['user']['id'], self.contact_client.id)
        self.assertEqual(response['user_info']['user']['full_name'], self.contact_client.full_name)


class GetClientTestCase(BaseSetUpConfig):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.details = 'get_client'
        cls.data_key_name = 'user_info'

    def test_get_client(self):
        response = processes.get_client(
            messenger_id=self.valid_messenger_id,
            transport_name=self.transport_name,
        )
        self.assertEqual(self.details, response[self.details_key_name])
        data_dict = response[self.data_key_name]
        self.assertEqual(self.contact_client.as_dict(), data_dict['user'])
        self.assertEqual(self.contact.as_dict(), data_dict['contact'])


class TokenNewTestCase(BaseSetUpConfig):
    outline_token_id_new_client = 9999
    outline_token_id_new_admin_anonim = 8888
    outline_token_id_new_admin_client = 7777

    @classmethod
    def setUpTestData(cls) -> None:
        cls.details_client = 'new_token by client'
        cls.details_admin = 'new_token by admin'
        cls.data_key_name = 'tokens'

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    @patch("requests.put", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.post", return_value=mocks.MockResponseCreateKey(outline_id=outline_token_id_new_client))
    def test_token_new_ok(self, *args):
        response = processes.token_new(
            transport_name=self.transport_name,
            server_name=self.server_name,
            credentials=self.credentials,
            tariff_name=self.tariff.name,
        )
        token_dict = response[self.data_key_name][0]
        self.assertEqual(response[self.details_key_name], self.details_client)
        self.assertEqual(token_dict['outline_id'], self.outline_token_id_new_client)
        self.assertTrue(token_dict['is_active'])
        self.assertFalse(token_dict['is_tech'])
        self.assertEqual(self.contact_client.as_dict(), response['user_info']['user'])

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    @patch("requests.put", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.post", return_value=mocks.MockResponseCreateKey(outline_id=outline_token_id_new_admin_anonim))
    def test_token_new_admin_ok_anonim(self, *args):
        response = processes.token_new(
            server_name=self.server_name,
            tariff_name=self.tariff.name,
        )
        token_dict = response[self.data_key_name][0]
        self.assertEqual(response[self.details_key_name], self.details_admin)
        self.assertEqual(token_dict['outline_id'], self.outline_token_id_new_admin_anonim)
        self.assertTrue(token_dict['is_active'])
        self.assertFalse(token_dict['is_tech'])
        self.assertEqual(Client.objects.last().as_dict(), response['user_info']['user'])

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    @patch("requests.put", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.post", return_value=mocks.MockResponseCreateKey(outline_id=outline_token_id_new_admin_client))
    def test_token_new_admin_ok_client(self, *args):
        cnt_clients_before = Client.objects.count()
        response = processes.token_new(
            server_name=self.server_name,
            tariff_name=self.tariff.name,
            client=self.contact_client,
        )
        cnt_clients_after = Client.objects.count()
        self.assertEqual(cnt_clients_after, cnt_clients_before)
        token_dict = response[self.data_key_name][0]
        self.assertEqual(response[self.details_key_name], self.details_admin)
        self.assertEqual(token_dict['outline_id'], self.outline_token_id_new_admin_client)
        self.assertTrue(token_dict['is_active'])
        self.assertFalse(token_dict['is_tech'])
        self.assertEqual(self.contact_client.as_dict(), response['user_info']['user'])

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_token_new_admin_demo_not_allowed(self, *args):
        with self.assertRaises(exceptions.DemoKeyNotAllowed) as err:
            processes.token_new(
                server_name=self.server_name,
                tariff_name=self.tariff_demo.name,
                client=self.contact_client,
            )
        self.assertEqual(
            'Cannot create demo key from admin',
            err.exception.message,
        )

    def test_token_new_vpn_server_does_not_exist(self):
        with self.assertRaises(exceptions.VPNServerDoesNotExist) as err:
            processes.token_new(
                transport_name=self.transport_name,
                server_name=self.not_exist_server_name,
                credentials=self.credentials,
                tariff_name=self.tariff.name,
            )
        self.assertEqual(
            f'VPN Server {self.not_exist_server_name!r} does not exist',
            err.exception.message,
        )

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_token_new_tariff_does_not_exist(self, *args):
        with self.assertRaises(exceptions.TariffDoesNotExist) as err:
            processes.token_new(
                transport_name=self.transport_name,
                server_name=self.server_name,
                credentials=self.credentials,
                tariff_name=self.not_exist_tariff_name,
            )
        self.assertEqual(
            f'Tariff {self.not_exist_tariff_name!r} does not exist',
            str(err.exception.message)
        )

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_token_new_demo_key_exist(self, *args):
        with self.assertRaises(exceptions.DemoKeyExist) as err:
            processes.token_new(
                transport_name=self.transport_name,
                server_name=self.server_name,
                credentials=self.credentials,
                tariff_name=self.tariff_demo.name,
            )
        self.assertEqual(
            f'User already have demo key',
            err.exception.message,
        )

    @patch("requests.post", return_value=mocks.MockResponseStatusCode404())
    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_token_new_vpn_server_response_error(self, *args):
        with self.assertRaises(exceptions.VPNServerResponseError) as err:
            processes.token_new(
                transport_name=self.transport_name,
                server_name=self.server_name,
                credentials=self.credentials,
                tariff_name=self.tariff.name,
            )
        self.assertEqual(
            f'Outline client error occurred due create key '
            f'new_token=<VPNToken id={VPNToken.objects.last().id} outline_id=None>',
            err.exception.message,
        )


class TokenRenewTestCase(BaseSetUpConfig):
    outline_token_id_renew_client = 9999
    outline_token_id_renew_admin = 8888

    @classmethod
    def setUpTestData(cls) -> None:
        cls.details_client = 'renew_token by client'
        cls.details_admin = 'renew_token by admin'
        cls.data_key_name = 'tokens'

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    @patch("requests.delete", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.put", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.post", return_value=mocks.MockResponseCreateKey(outline_id=outline_token_id_renew_client))
    def test_token_renew_ok(self, *args):
        self.assertTrue(self.vpn_token.is_active)
        response = processes.token_renew(
            transport_name=self.transport_name,
            credentials=self.credentials,
            token_id=self.vpn_token.id,
        )
        self.assertEqual(self.details_client, response[self.details_key_name])
        data_dict = response[self.data_key_name][0]
        self.vpn_token.refresh_from_db()
        self.assertFalse(self.vpn_token.is_active)
        self.assertEqual(self.vpn_token.id, data_dict['previous_vpn_token_id'])
        self.assertEqual(data_dict['outline_id'], self.outline_token_id_renew_client)
        renewed_token = VPNToken.objects.last()
        self.assertEqual(renewed_token.id, data_dict['id'])
        self.assertTrue(renewed_token.is_active)
        self.assertEqual(data_dict, renewed_token.as_dict())
        self.assertEqual(self.contact_client.as_dict(), response['user_info']['user'])
        self.assertEqual(self.contact.as_dict(), response['user_info']['contact'])

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    @patch("requests.delete", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.put", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.post", return_value=mocks.MockResponseCreateKey(outline_id=outline_token_id_renew_admin))
    def test_token_renew_admin_ok(self, *args):
        self.assertTrue(self.vpn_token.is_active)
        result = processes.token_renew(
            token_id=self.vpn_token.id,
        )
        self.assertEqual(self.details_admin, result[self.details_key_name])
        data_dict = result[self.data_key_name][0]
        self.vpn_token.refresh_from_db()
        self.assertFalse(self.vpn_token.is_active)
        self.assertEqual(self.vpn_token.id, data_dict['previous_vpn_token_id'])
        self.assertEqual(data_dict['outline_id'], self.outline_token_id_renew_admin)
        renewed_token = VPNToken.objects.last()
        self.assertEqual(renewed_token.id, data_dict['id'])
        self.assertTrue(renewed_token.is_active)
        self.assertEqual(data_dict, renewed_token.as_dict())
        self.assertEqual(self.contact_client.as_dict(), result['user_info']['user'])

    def test_token_renew_belong_to_another_user(self):
        with self.assertRaises(exceptions.BelongToAnotherUser) as err:
            processes.token_renew(
                transport_name=self.transport_name,
                credentials=self.credentials,
                token_id=self.invalid_token_id,
            )
        self.assertEqual('Error token renew. Token belongs to another user.', err.exception.message)

    def test_token_renew_renew_demo_key_not_allowed(self):
        with self.assertRaises(exceptions.DemoKeyNotAllowed) as err:
            processes.token_renew(
                transport_name=self.transport_name,
                credentials=self.credentials,
                token_id=self.vpn_token_demo.id,
            )
        self.assertEqual('Error token renew. Cannot renew demo key.', err.exception.message)

    def test_token_renew_vpn_key_not_active(self):
        self.vpn_token.is_active = False
        self.vpn_token.save()
        with self.assertRaises(exceptions.VPNTokenIsNotActive) as err:
            processes.token_renew(
                transport_name=self.transport_name,
                credentials=self.credentials,
                token_id=self.vpn_token.id,
            )
        self.assertEqual('Error token renew. Token is not active and not exist on VPN server', err.exception.message)

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    @patch("requests.post", return_value=mocks.MockResponseStatusCode404())
    def test_token_renew_vpn_server_response_error(self, *args):
        with self.assertRaises(exceptions.VPNServerResponseError) as err:
            processes.token_renew(
                transport_name=self.transport_name,
                credentials=self.credentials,
                token_id=self.vpn_token.id,
            )
        self.assertIn('Outline client error occurred due create key', err.exception.message)


class GetTariffTestCase(BaseSetUpConfig):
    @classmethod
    def setUpTestData(cls):
        cls.details = 'get_tariff'
        cls.data_key_name = 'tariffs'

    def test_get_tariffications(self):
        response = processes.get_tariff()
        self.assertEqual(len(response[self.data_key_name]), Tariff.objects.filter(is_active=True).count())
        self.assertEqual(self.details, response[self.details_key_name])


class GetVPNServersTestCase(BaseSetUpConfig):
    @classmethod
    def setUpTestData(cls):
        cls.details = 'get_vpn_servers'
        cls.data_key_name = 'vpn_servers'

    def test_get_vpn_servers(self):
        response = processes.get_vpn_servers()
        self.assertEqual(len(response[self.data_key_name]), VPNServer.objects.filter(is_active=True).count())
        self.assertEqual(self.details, response[self.details_key_name])


class GetTransportsTestCase(BaseSetUpConfig):
    @classmethod
    def setUpTestData(cls):
        cls.details = 'get_transports'
        cls.data_key_name = 'transports'

    def test_get_transports(self):
        response = processes.get_transports()
        self.assertEqual(len(response[self.data_key_name]), Transport.objects.filter(is_active=True).count())
        self.assertEqual(self.details, response[self.details_key_name])


class GetTokenTestCase(BaseSetUpConfig):
    def test_get_token_ok(self):
        response = processes.get_token(self.vpn_token.id)
        self.assertEqual(self.vpn_token, response)

    def test_get_token_does_not_exist(self):
        with self.assertRaises(exceptions.VPNTokenDoesNotExist) as err:
            processes.get_token(self.invalid_token_id)
        self.assertIn(f'VPN Token id={self.invalid_token_id!r} does not exist', err.exception.message)


class GetTokenInfoTestCase(BaseSetUpConfig):
    @classmethod
    def setUpTestData(cls):
        cls.details = 'get_token_info'
        cls.data_key_name = 'tokens'

    def test_get_token_info(self):
        response = processes.get_token_info(self.vpn_token.id)
        self.assertEqual(self.details, response[self.details_key_name])
        data_dict = response[self.data_key_name][0]
        vpn_token_dict = self.vpn_token.as_dict()
        if vpn_token_dict['valid_until']:
            vpn_token_dict['valid_until'] = vpn_token_dict['valid_until'].strftime(DATE_STRING_FORMAT)
        self.assertEqual(data_dict, vpn_token_dict)


class AddTrafficLimitTestCase(BaseSetUpConfig):
    @classmethod
    def setUpTestData(cls):
        cls.details = 'traffic_limit_updated'
        cls.data_key_name = 'tokens'

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    @patch("requests.put", return_value=mocks.MockResponseStatusCode204())
    def test_add_traffic_limit_ok(self, *args):
        self.assertIsNone(self.vpn_token.traffic_limit)
        response = processes.add_traffic_limit(self.vpn_token.id, self.traffic_limit_in_bytes)
        self.assertEqual(self.details, response[self.details_key_name])
        data_dict = response[self.data_key_name][0]
        self.vpn_token.refresh_from_db()
        self.assertIsNotNone(self.vpn_token.traffic_limit)
        self.assertEqual(self.vpn_token.traffic_limit, self.traffic_limit_in_bytes)
        self.assertEqual(self.vpn_token.traffic_limit, data_dict['traffic_limit'])

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    @patch("requests.put", return_value=mocks.MockResponseStatusCode404())
    def test_add_traffic_limit_vpn_server_response_error(self, *args):
        self.assertIsNone(self.vpn_token.traffic_limit)
        with self.assertRaises(exceptions.VPNServerResponseError) as err:
            processes.add_traffic_limit(self.vpn_token.id, self.traffic_limit_in_bytes)
        self.assertEqual('Outline client error occurred due traffic limit add', err.exception.message)
        self.vpn_token.refresh_from_db()
        self.assertIsNone(self.vpn_token.traffic_limit)


class DelTrafficLimitTestCase(BaseSetUpConfig):
    @classmethod
    def setUpTestData(cls):
        cls.details = 'traffic_limit_removed'
        cls.data_key_name = 'tokens'

    @patch("requests.delete", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_del_traffic_limit_ok(self, *args):
        self.assertIsNone(self.vpn_token.traffic_limit)
        self.vpn_token.traffic_limit = self.traffic_limit_in_bytes
        self.vpn_token.save()
        response = processes.del_traffic_limit(self.vpn_token.id)
        self.assertEqual(self.details, response[self.details_key_name])
        data_dict = response[self.data_key_name][0]
        self.vpn_token.refresh_from_db()
        self.assertEqual(data_dict['traffic_limit'], self.vpn_token.traffic_limit)

    @patch("requests.delete", return_value=mocks.MockResponseStatusCode404())
    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_del_traffic_limit_vpn_server_response_error(self, *args):
        self.assertIsNone(self.vpn_token.traffic_limit)
        self.vpn_token.traffic_limit = self.traffic_limit_in_bytes
        self.vpn_token.save()
        with self.assertRaises(exceptions.VPNServerResponseError) as err:
            processes.del_traffic_limit(self.vpn_token.id)
        self.assertEqual('Outline client error occurred due traffic limit delete', err.exception.message)
        self.vpn_token.refresh_from_db()
        self.assertEqual(self.vpn_token.traffic_limit, self.traffic_limit_in_bytes)


class ChangeVPNTokenTrafficLimitTestCase(BaseSetUpConfig):
    def test_change_vpn_token_traffic_limit_ok_none(self):
        self.assertFalse(self.vpn_token.traffic_limit)
        self.vpn_token.traffic_limit = self.traffic_limit_in_bytes
        self.vpn_token.save()
        response = processes.change_vpn_token_traffic_limit(self.vpn_token, 0)
        self.vpn_token.refresh_from_db()
        vpn_token_dict = self.vpn_token.as_dict()
        if vpn_token_dict['valid_until']:
            vpn_token_dict['valid_until'] = vpn_token_dict['valid_until'].strftime(DATE_STRING_FORMAT)
        self.assertEqual(response, vpn_token_dict)

    def test_change_vpn_token_traffic_limit_ok_add(self):
        self.assertFalse(self.vpn_token.traffic_limit)
        response = processes.change_vpn_token_traffic_limit(self.vpn_token, 0)
        self.vpn_token.refresh_from_db()
        vpn_token_dict = self.vpn_token.as_dict()
        if vpn_token_dict['valid_until']:
            vpn_token_dict['valid_until'] = vpn_token_dict['valid_until'].strftime(DATE_STRING_FORMAT)
        self.assertEqual(response, vpn_token_dict)


class DelOutlineVPNKeyTestCase(BaseSetUpConfig):
    @classmethod
    def setUpTestData(cls):
        cls.details = 'vpn_token_deleted'
        cls.data_key_name = 'tokens'

    @patch("requests.delete", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_del_outline_vpn_key_ok(self, *args):
        self.assertTrue(self.vpn_token.is_active)
        response = processes.del_outline_vpn_key(self.vpn_token.id)
        self.assertEqual(self.details, response[self.details_key_name])
        data_dict = response[self.data_key_name][0]
        self.vpn_token.refresh_from_db()
        self.assertFalse(self.vpn_token.is_active)
        self.assertFalse(data_dict['is_active'])
        self.assertIn('Deleted', data_dict['name'])

    @patch("requests.delete", return_value=mocks.MockResponseStatusCode404())
    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_del_outline_vpn_key_vpn_server_response_error(self, *args):
        self.assertTrue(self.vpn_token.is_active)
        with self.assertRaises(exceptions.VPNServerResponseError) as err:
            processes.del_outline_vpn_key(self.vpn_token.id)
        self.assertEqual('Outline client error occurred due key delete', err.exception.message)
        self.vpn_token.refresh_from_db()
        self.assertTrue(self.vpn_token.is_active)


class ChangeVPNTokenActiveStatusTestCase(BaseSetUpConfig):
    def test_change_vpn_token_active_state_false(self):
        self.assertTrue(self.vpn_token.is_active)
        response = processes.change_vpn_token_active_state(self.vpn_token)
        self.vpn_token.refresh_from_db()
        self.assertFalse(self.vpn_token.is_active)
        self.assertIn('Deleted', self.vpn_token.name)
        vpn_token_dict = self.vpn_token.as_dict()
        if vpn_token_dict['valid_until']:
            vpn_token_dict['valid_until'] = vpn_token_dict['valid_until'].strftime(DATE_STRING_FORMAT)
        self.assertEqual(response, vpn_token_dict)

    def test_change_vpn_token_active_state_true(self):
        self.assertTrue(self.vpn_token.is_active)
        self.vpn_token.is_active = False
        self.vpn_token.save()
        response = processes.change_vpn_token_active_state(self.vpn_token)
        self.vpn_token.refresh_from_db()
        self.assertFalse(self.vpn_token.is_active)
        vpn_token_dict = self.vpn_token.as_dict()
        if vpn_token_dict['valid_until']:
            vpn_token_dict['valid_until'] = vpn_token_dict['valid_until'].strftime(DATE_STRING_FORMAT)
        self.assertEqual(response, vpn_token_dict)


class TelegramMessageSenderTestCase(BaseSetUpConfig):
    @classmethod
    def setUpTestData(cls):
        cls.send_text = 'Test message'
        cls.details_personal = 'personal_message_send'
        cls.details_all = 'all_users_message_send'
        cls.data_key_name = 'info'

    @patch('telebot.TeleBot.send_message', return_value=mocks.MockResponseStatusCode200())
    def test_telegram_message_sender_ok_personal(self, *args):
        response = processes.telegram_message_sender(
            transport_name=self.transport_name,
            text=self.send_text,
            messenger_id=self.valid_messenger_id,
        )
        self.assertEqual(self.details_personal, response[self.details_key_name])
        data_dict = response[self.data_key_name]
        self.assertEqual(data_dict['success'], 1)

    @patch('telebot.TeleBot.send_message', return_value=mocks.MockResponseStatusCode200())
    def test_telegram_message_sender_ok_all_users(self, *args):
        helpers.create_contact(
            client=helpers.create_client()[0],
            transport=self.transport,
            credentials=self.new_contact_credentials
        )
        response = processes.telegram_message_sender(
            transport_name=self.transport_name,
            text=self.send_text,
        )
        self.assertEqual(self.details_all, response[self.details_key_name])
        data_dict = response[self.data_key_name]
        self.assertEqual(data_dict['success'], 2)
        self.assertEqual(data_dict['error'], 0)

    def test_telegram_message_sender_transport_does_not_exist(self):
        with self.assertRaises(exceptions.TransportDoesNotExist) as err:
            processes.telegram_message_sender(
                transport_name=self.not_exist_transport_name,
                text=self.send_text,
                messenger_id=self.valid_messenger_id,
            )
        self.assertEqual(f'Transport {self.not_exist_transport_name!r} does not exist', err.exception.message)

    # @patch('telebot.TeleBot.send_message', return_value=mocks.MockResponseStatusCode404())
    # def test_telegram_message_sender_personal_transport_message_send_error(self, *args):
    #     with self.assertRaises(exceptions.TransportMessageSendError) as err:
    #         processes.telegram_message_sender(
    #             transport_name=self.transport_name,
    #             text=self.send_text,
    #             messenger_id=self.invalid_messenger_id,
    #         )
    #     self.assertIn(self.transport_name, err.exception.message)


class UpdateTokenValidUntilTestCase(BaseSetUpConfig):
    @classmethod
    def setUpTestData(cls):
        cls.days = 30
        cls.details = 'token_valid_until_updated'
        cls.data_key_name = 'tokens'

    def test_update_token_valid_until_ok_date(self):
        self.assertIsNone(self.vpn_token.valid_until)
        response = processes.update_token_valid_until(self.vpn_token.id, self.days)
        self.assertEqual(self.details, response[self.details_key_name])
        data_dict = response[self.data_key_name][0]
        self.vpn_token.refresh_from_db()
        vpn_token_dict = self.vpn_token.as_dict()
        if vpn_token_dict['valid_until']:
            vpn_token_dict['valid_until'] = vpn_token_dict['valid_until'].strftime(DATE_STRING_FORMAT)
        self.assertEqual(data_dict, vpn_token_dict)

    def test_update_token_valid_until_ok_none(self):
        self.assertIsNone(self.vpn_token.valid_until)
        self.vpn_token.valid_until = datetime.datetime.now()
        self.vpn_token.save()
        response = processes.update_token_valid_until(self.vpn_token.id, 0)
        self.assertEqual(self.details, response[self.details_key_name])
        data_dict = response[self.data_key_name][0]
        self.vpn_token.refresh_from_db()
        vpn_token_dict = self.vpn_token.as_dict()
        if vpn_token_dict['valid_until']:
            vpn_token_dict['valid_until'] = vpn_token_dict['valid_until'].strftime(DATE_STRING_FORMAT)
        self.assertEqual(data_dict, vpn_token_dict)

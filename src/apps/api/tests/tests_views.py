import datetime
import apps.outline_vpn_admin.tests.helpers as helpers
from vpnservice.settings import DATE_STRING_FORMAT
from unittest.mock import patch
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.urls import reverse
from rest_framework.test import APITestCase
from apps.outline_vpn_admin.models import Tariff, VPNServer, Contact, VPNToken, Client, Transport
from apps.outline_vpn_admin.tests import mocks as mocks


class BaseAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.status_OK = 200
        self.status_CREATED = 201
        self.status_NOT_FOUND = 404
        self.status_FORBIDDEN = 403
        self.status_UNAUTHORIZED = 401
        self.status_SERVICE_UNAVAILABLE = 503
        self.not_exist_transport = 'not_exist'
        self.bot = User.objects.create(
            username='test',
            password='test',
            email='test@test.ru'
        )
        self.bot.save()
        self.invalid_token_id = 9999999
        self.token = Token.objects.get(user_id=self.bot.id).key
        self.HTTP_AUTHORIZATION = f"Token  {self.token}"
        self.contact_client = helpers.create_client()[0]
        self.transport_name = 'test'
        self.transport_cnt = Transport.objects.all().count()
        self.transport = helpers.create_transport(transport_name=self.transport_name)[0]
        self.credentials = {'id': 9999999, 'phone_number': 9999, 'first_name': 'test', 'last_name': 'test'}
        self.contact = helpers.create_contact(
            client=self.contact_client,
            transport=self.transport,
            credentials=self.credentials
        )

        self.tariffs = helpers.create_tariff(
            cnt=2,
            currency=helpers.create_currency()[0]
        )
        self.tariffs[0].is_demo = True
        self.tariffs[0].save()
        self.tariff_demo = self.tariffs[0]
        self.tariff = self.tariffs[1]
        self.server_name = 'test_server_name'
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


class GetActualCacheDateTest(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('api:get_actual_cache_date')
        cls.details = 'get_actual_cache_date'
        cls.data_key_name = 'cache_update_date'

    def test_get_actual_cache_date_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        response = self.client.get(self.url, format='json')
        self.assertEqual(self.status_OK, response.status_code)
        data_dict = response.json()
        self.assertIn(data_dict['details'], self.details)
        self.assertIsNotNone(data_dict.get(self.data_key_name))

    def test_get_tariff_no_auth(self):
        self.client.credentials()
        response = self.client.get(self.url, format='json')
        self.assertEqual(self.status_UNAUTHORIZED, response.status_code)


class TariffTest(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('api:get_tariffs')
        cls.details = 'get_tariffs'
        cls.data_key_name = 'tariffs'

    def test_get_tariff_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        response = self.client.get(self.url, format='json')
        tariffs = Tariff.objects.all().count()
        data_dict = response.json()
        self.assertEqual(self.status_OK, response.status_code)
        self.assertIn(data_dict['details'], self.details)
        self.assertEqual(len(data_dict.get(self.data_key_name)), tariffs)

    def test_get_tariff_no_auth(self):
        self.client.credentials()
        response = self.client.get(self.url, format='json')
        self.assertEqual(self.status_UNAUTHORIZED, response.status_code)


class VPNServerTest(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('api:get_vpn_servers')
        cls.details = 'get_vpn_servers'
        cls.data_key_name = 'vpn_servers'

    def test_get_vpn_servers_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        response = self.client.get(self.url, format='json')
        vpn_servers = VPNServer.objects.all().count()
        data_dict = response.json()
        self.assertEqual(self.status_OK, response.status_code)
        self.assertIn(data_dict['details'], self.details)
        self.assertEqual(len(data_dict.get(self.data_key_name)), vpn_servers)

    def test_get_vpn_servers_no_auth(self):
        self.client.credentials()
        response = self.client.get(self.url, format='json')
        self.assertEqual(self.status_UNAUTHORIZED, response.status_code)


class ContactCreateOrUpdateTest(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url_get = 'api:get_cont'
        cls.details_get = 'get_client'
        cls.url_post = reverse('api:creat_or_update_contact')
        cls.details_post_create = 'Created new user'
        cls.details_post_update = 'Updated exist user'
        cls.data_key_name = 'user_info'

    def test_get_client_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        url_get = reverse(self.url_get, args=[self.transport_name, self.credentials['id']])
        response = self.client.get(url_get, format='json')
        data_dict = response.json()
        self.assertEqual(self.status_OK, response.status_code)
        self.assertIn(self.details_get, data_dict.get('details'))
        self.assertTrue(data_dict.get(self.data_key_name))

    def test_get_client_no_auth(self):
        self.client.credentials()
        url_get = reverse(self.url_get, args=[self.transport_name, self.credentials['id']])
        response = self.client.get(url_get, format='json')
        self.assertEqual(self.status_UNAUTHORIZED, response.status_code)

    def test_get_client_transport_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        url_get = reverse(self.url_get, args=[self.not_exist_transport, self.credentials['id']])
        response = self.client.get(url_get, format='json')
        self.assertEqual(self.status_NOT_FOUND, response.status_code)
        self.assertIn(f"Transport {self.not_exist_transport!r} does not exist", response.json()['details'])

    def test_get_client_user_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        url_get = reverse(self.url_get, args=[self.transport_name, 999999999])
        response = self.client.get(url_get, format='json')
        self.assertEqual(self.status_NOT_FOUND, response.status_code)
        self.assertIn('User does not exist', response.json()['details'])

    def test_create_or_update_contact_create_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        new_messenger_id = 252525
        self.credentials['id'] = new_messenger_id
        send_data = {
            'transport_name': self.transport_name,
            'credentials': self.credentials,
        }
        response = self.client.post(self.url_post, data=send_data, format='json')
        self.assertEqual(self.status_CREATED, response.status_code)
        data_dict = response.json()
        self.assertIn(self.details_post_create, data_dict['details'])
        self.assertEqual(new_messenger_id, data_dict['user_info']['contact']['credentials']['id'])
        self.assertEqual(2, Contact.objects.all().count())

    def test_create_or_update_contact_update_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        new_last_name = 'updated'
        self.credentials['last_name'] = new_last_name
        send_data = {
            'transport_name': self.transport_name,
            'credentials': self.credentials,
        }
        response = self.client.post(self.url_post, data=send_data, format='json')
        self.assertEqual(self.status_OK, response.status_code)
        data_dict = response.json()
        self.assertIn(self.details_post_update, data_dict['details'])
        self.assertIn(new_last_name, data_dict['user_info']['contact']['credentials']['last_name'])
        self.assertEqual(1, Contact.objects.all().count())

    def test_create_or_update_contact_transport_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        send_data = {
            'transport_name': self.not_exist_transport,
            'credentials': self.credentials,
        }
        response = self.client.post(self.url_post, data=send_data, format='json')
        self.assertEqual(self.status_NOT_FOUND, response.status_code)
        self.assertIn(f"Transport {self.not_exist_transport!r} does not exist", response.json()['details'])

    def test_create_or_update_contact_no_auth(self):
        self.client.credentials()
        response = self.client.post(self.url_post, format='json')
        self.assertEqual(self.status_UNAUTHORIZED, response.status_code)


class VPNTokenNewTest(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('api:create_new_token')
        cls.details = 'new_token'
        cls.data_key_name = 'tokens'

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    @patch("requests.put", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.post", return_value=mocks.MockResponseCreateKey())
    def test_vpn_token_new_ok(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        send_data = {
            'transport_name': self.transport_name,
            'credentials': self.credentials,
            'server_name': self.server_name,
            'tariff_name': self.tariff.name,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        self.assertEqual(self.status_CREATED, response.status_code)
        data_dict = response.json()
        self.assertIn(self.details, data_dict['details'])
        self.assertFalse(data_dict['tokens'][0]['is_demo'])
        self.assertEqual(1, len(data_dict.get(self.data_key_name)))
        self.assertEqual(3, VPNToken.objects.all().count())

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_vpn_token_demo_key_not_allowed(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        send_data = {
            'transport_name': None,
            'credentials': None,
            'server_name': self.server_name,
            'tariff_name': self.tariff_demo.name,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        self.assertEqual(self.status_FORBIDDEN, response.status_code)
        data_dict = response.json()
        self.assertEqual("Cannot create demo key from admin", data_dict['details'])

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    @patch("requests.put", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.post", return_value=mocks.MockResponseCreateKey())
    def test_vpn_token_key_admin_ok(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        send_data = {
            'transport_name': None,
            'credentials': None,
            'server_name': self.server_name,
            'tariff_name': self.tariff.name,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        self.assertEqual(self.status_CREATED, response.status_code)
        data_dict = response.json()
        self.assertIn(self.details, data_dict['details'])
        self.assertFalse(data_dict['tokens'][0]['is_demo'])
        self.assertEqual(1, len(data_dict.get(self.data_key_name)))
        self.assertEqual(
            data_dict['tokens'][0]['client'],
            Client.objects.all().last().id,
        )

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_vpn_token_demo_exist(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        send_data = {
            'transport_name': self.transport_name,
            'credentials': self.credentials,
            'server_name': self.server_name,
            'tariff_name': self.tariff_demo.name,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        self.assertEqual(self.status_FORBIDDEN, response.status_code)
        data_dict = response.json()
        self.assertEqual("User already have demo key", data_dict['details'])

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    @patch("requests.put", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.post", return_value=mocks.MockResponseCreateKey())
    def test_vpn_token_demo_new_ok(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        new_cred = {'id': 987654321, 'phone_number': 987654321, 'first_name': 'test', 'last_name': 'test'}
        helpers.create_contact(
            client=helpers.create_client()[0],
            transport=self.transport,
            credentials=new_cred,
        )
        send_data = {
            'transport_name': self.transport_name,
            'credentials': new_cred,
            'server_name': self.server_name,
            'tariff_name': self.tariff_demo.name,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        self.assertEqual(self.status_CREATED, response.status_code)
        data_dict = response.json()
        self.assertIn(self.details, data_dict['details'])
        self.assertTrue(data_dict['tokens'][0]['is_demo'])
        self.assertEqual(1, len(data_dict.get(self.data_key_name)))
        self.assertEqual(3, VPNToken.objects.all().count())

    def test_vpn_token_new_no_auth(self):
        self.client.credentials()
        response = self.client.post(self.url, format='json')
        self.assertEqual(self.status_UNAUTHORIZED, response.status_code)

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_vpn_token_new_transport_does_not_exist(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        send_data = {
            'transport_name': self.not_exist_transport,
            'credentials': self.credentials,
            'server_name': self.server_name,
            'tariff_name': self.tariff.name,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        self.assertEqual(self.status_NOT_FOUND, response.status_code)
        data_dict = response.json()
        self.assertEqual(f"Transport {self.not_exist_transport!r} does not exist", data_dict['details'])

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_vpn_token_new_user_does_not_exist(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        self.credentials['id'] = 909090909090
        send_data = {
            'transport_name': self.transport_name,
            'credentials': self.credentials,
            'server_name': self.server_name,
            'tariff_name': self.tariff.name,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        self.assertEqual(self.status_NOT_FOUND, response.status_code)
        data_dict = response.json()
        self.assertEqual('User does not exist', data_dict['details'])

    def test_vpn_token_new_vpn_server_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        new_cred = {'id': 3213123, 'phone_number': 31231, 'first_name': 'test', 'last_name': 'test'}
        helpers.create_contact(
            client=helpers.create_client()[0],
            transport=self.transport,
            credentials=new_cred,
        )
        send_data = {
            'transport_name': self.transport_name,
            'credentials': new_cred,
            'server_name': 'not exist',
            'tariff_name': self.tariff_demo.as_dict(),
        }
        response = self.client.post(self.url, data=send_data, format='json')
        self.assertEqual(self.status_NOT_FOUND, response.status_code)
        data_dict = response.json()
        self.assertEqual("VPN Server 'not exist' does not exist", data_dict['details'])

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_vpn_token_new_tariff_does_not_exist(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        send_data = {
            'transport_name': self.transport_name,
            'credentials': self.credentials,
            'server_name': self.server_name,
            'tariff_name': 'not exist',
        }
        response = self.client.post(self.url, data=send_data, format='json')
        self.assertEqual(self.status_NOT_FOUND, response.status_code)
        data_dict = response.json()
        self.assertEqual("Tariff 'not exist' does not exist", data_dict['details'])

    @patch("requests.get", return_value=mocks.MockResponseStatusCode404())
    def test_vpn_token_new_vpn_server_response_error(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        send_data = {
            'transport_name': self.transport_name,
            'credentials': self.credentials,
            'server_name': self.server_name,
            'tariff_name': self.tariff.name,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        self.assertEqual(self.status_SERVICE_UNAVAILABLE, response.status_code)

    @patch("requests.post", return_value=mocks.MockResponseStatusCode404())
    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_vpn_token_new_vpn_server_does_not_response(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        send_data = {
            'transport_name': self.transport_name,
            'credentials': self.credentials,
            'server_name': self.server_name,
            'tariff_name': self.tariff.name,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        self.assertEqual(self.status_SERVICE_UNAVAILABLE, response.status_code)
        self.assertEqual(VPNToken.objects.all().count(), 3)


class VPNTokenReNewTest(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('api:renew_exist_token')
        cls.details = 'renew_token'
        cls.data = 'tokens'

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    @patch("requests.delete", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.put", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.post", return_value=mocks.MockResponseCreateKey())
    def test_vpn_token_renew_ok(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        send_data = {
            'transport_name': self.transport_name,
            'credentials': self.credentials,
            'token_id': self.vpn_token.id,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        data_dict = response.json()
        self.assertEqual(self.status_CREATED, response.status_code)
        self.assertIn(self.details, data_dict.get('details'))
        old_token = VPNToken.objects.get(id=self.vpn_token.id)
        self.assertEqual(self.vpn_token.id, data_dict['tokens'][0]['previous_vpn_token_id'])
        self.assertIn('Renewed', old_token.name)
        self.assertFalse(old_token.is_active)
        new_token = VPNToken.objects.last()
        self.assertNotEqual(old_token.id, new_token.id)
        self.assertEqual(3, VPNToken.objects.all().count())
        self.assertEqual(2, VPNToken.objects.filter(is_active=True).count())

    def test_vpn_token_renew_no_auth(self):
        self.client.credentials()
        response = self.client.post(self.url, format='json')
        self.assertEqual(self.status_UNAUTHORIZED, response.status_code)

    def test_vpn_token_renew_transport_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        send_data = {
            'transport_name': self.not_exist_transport,
            'credentials': self.credentials,
            'token_id': self.vpn_token.id,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        self.assertEqual(self.status_NOT_FOUND, response.status_code)
        data_dict = response.json()
        self.assertEqual(f"Transport {self.not_exist_transport!r} does not exist", data_dict['details'])

    def test_vpn_token_renew_user_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        self.credentials['id'] = 909090909090
        send_data = {
            'transport_name': self.transport_name,
            'credentials': self.credentials,
            'token_id': self.vpn_token.id,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        self.assertEqual(self.status_NOT_FOUND, response.status_code)
        data_dict = response.json()
        self.assertEqual('User does not exist', data_dict['details'])

    def test_vpn_token_renew_belong_to_another_user(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        send_data = {
            'transport_name': self.transport_name,
            'credentials': self.credentials,
            'token_id': self.invalid_token_id,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        data_dict = response.json()
        self.assertEqual(self.status_FORBIDDEN, response.status_code)
        self.assertEqual('Error token renew. Token belongs to another user.', data_dict.get('details'))

    def test_vpn_token_renew_demo_key_not_possible(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        send_data = {
            'transport_name': self.transport_name,
            'credentials': self.credentials,
            'token_id': self.vpn_token_demo.id,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        data_dict = response.json()
        self.assertEqual(self.status_FORBIDDEN, response.status_code)
        self.assertEqual('Error token renew. Cannot renew demo key.', data_dict.get('details'))

    @patch("requests.get", return_value=mocks.MockResponseStatusCode404())
    def test_vpn_token_renew_vpn_server_response_error(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        send_data = {
            'transport_name': self.transport_name,
            'credentials': self.credentials,
            'token_id': self.vpn_token.id,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        self.assertEqual(self.status_SERVICE_UNAVAILABLE, response.status_code)

    @patch("requests.post", return_value=mocks.MockResponseStatusCode404())
    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_vpn_token_renew_vpn_server_does_not_response(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        send_data = {
            'transport_name': self.transport_name,
            'credentials': self.credentials,
            'token_id': self.vpn_token.id,
        }
        response = self.client.post(self.url, data=send_data, format='json')
        self.assertEqual(self.status_SERVICE_UNAVAILABLE, response.status_code)
        self.assertEqual(VPNToken.objects.all().count(), 3)


class VPNTokensTest(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = 'api:get_client_tokens'
        cls.details = 'client_tokens'
        cls.data_key_name = 'tokens'

    def test_vpn_tokens_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        url = reverse(self.url, args=[self.transport_name, self.credentials['id']])
        response = self.client.get(url, format='json')
        data_dict = response.json()
        self.assertEqual(self.status_OK, response.status_code)
        self.assertIn(self.details, data_dict.get('details'))
        self.assertTrue(data_dict.get(self.data_key_name))
        self.assertEqual(2, len(data_dict.get(self.data_key_name)))

    def test_vpn_tokens_no_auth(self):
        self.client.credentials()
        uls = reverse(self.url, args=[self.transport_name, self.credentials['id']])
        response = self.client.get(uls, format='json')
        self.assertEqual(self.status_UNAUTHORIZED, response.status_code)

    def test_vpn_tokens_transport_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        url_get = reverse(self.url, args=[self.not_exist_transport, self.credentials['id']])
        response = self.client.get(url_get, format='json')
        self.assertEqual(self.status_NOT_FOUND, response.status_code)
        self.assertIn(f"Transport {self.not_exist_transport!r} does not exist", response.json()['details'])

    def test_vpn_tokens_user_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        url_get = reverse(self.url, args=[self.transport_name, 999999999])
        response = self.client.get(url_get, format='json')
        self.assertEqual(self.status_NOT_FOUND, response.status_code)
        self.assertIn('User does not exist', response.json()['details'])


class VPNTokenGetTest(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = 'api:get_token_info'
        cls.details = 'get_token_info'
        cls.data_key_name = 'tokens'

    def test_get_vpn_token_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        url = reverse(self.url, args=[self.vpn_token.id])
        response = self.client.get(url, format='json')
        self.assertEqual(self.status_OK, response.status_code)
        json_data = response.json()
        self.assertEqual(self.details, json_data['details'])
        self.assertEqual(self.vpn_token.id, json_data[self.data_key_name][0]['id'])
        self.assertNotEqual(self.vpn_token_demo.id, json_data[self.data_key_name][0]['id'])

    def test_get_vpn_token_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        url = reverse(self.url, args=[self.invalid_token_id])
        response = self.client.get(url, format='json')
        self.assertEqual(self.status_NOT_FOUND, response.status_code)
        self.assertIn('does not exist', response.json()['details'])

    def test_get_vpn_token_no_auth(self):
        self.client.credentials()
        url = reverse(self.url, args=[self.vpn_token.id])
        response = self.client.get(url, format='json')
        self.assertEqual(self.status_UNAUTHORIZED, response.status_code)


class VPNTokenDeleteTest(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('api:delete_token')
        cls.details = 'VPN Token deleted'
        cls.data_key_name = 'tokens'

    @patch("requests.delete", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_delete_vpn_token_ok(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        json_to_send = {
            'token_id': self.vpn_token.id
        }
        response = self.client.delete(self.url, data=json_to_send, format='json')
        self.assertEqual(response.status_code, self.status_OK)
        json_data = response.json()
        self.assertEqual(self.details, json_data['details'])
        self.vpn_token.refresh_from_db()
        self.assertEqual(self.vpn_token.name, json_data[self.data_key_name][0]['name'])

    def test_delete_vpn_token_no_auth(self):
        self.client.credentials()
        json_to_send = {
            'token_id': self.vpn_token.id
        }
        response = self.client.delete(self.url, data=json_to_send, format='json')
        self.assertEqual(self.status_UNAUTHORIZED, response.status_code)

    @patch("requests.get", return_value=mocks.MockResponseStatusCode404())
    def test_delete_vpn_token_vpn_server_response_error(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        json_to_send = {
            'token_id': self.vpn_token.id
        }
        response = self.client.delete(self.url, data=json_to_send, format='json')
        self.assertEqual(response.status_code, self.status_SERVICE_UNAVAILABLE)

    def test_delete_vpn_token_vpn_server_does_not_exist(self):
        """Недостижимый сценарий, на VPN сервер foreign key из vpn_token и он заведомо существует,
        тк создать ключ без сервера невозможно"""
        pass

    @patch("requests.delete", return_value=mocks.MockResponseStatusCode404())
    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_delete_vpn_token_vpn_server_does_not_response(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        json_to_send = {
            'token_id': self.vpn_token.id
        }
        response = self.client.delete(self.url,data=json_to_send, format='json')
        self.assertEqual(response.status_code, self.status_SERVICE_UNAVAILABLE)

    def test_delete_vpn_token_vpn_token_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        json_to_send = {
            'token_id': self.invalid_token_id
        }
        response = self.client.delete(self.url, data=json_to_send, format='json')
        self.assertEqual(response.status_code, self.status_NOT_FOUND)


class VPNTokenPatchTest(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('api:update_token')
        cls.details_traffic_limit = 'Traffic limit updated'
        cls.details_valid_until = 'Token valid_until updated'
        cls.details_else = 'Traffic limit removed'
        cls.data_key_name = 'tokens'

    def test_vpn_token_patch_no_auth(self):
        self.client.credentials()
        response = self.client.patch(self.url, format='json')
        self.assertEqual(self.status_UNAUTHORIZED, response.status_code)

    @patch("requests.put", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_vpn_token_patch_traffic_limit_ok(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        traffic_limit_in_mb = 1024
        json_to_send = {
            'token_id': self.vpn_token.id,
            'traffic_limit': traffic_limit_in_mb
        }
        self.assertIsNone(self.vpn_token.traffic_limit)
        response = self.client.patch(self.url, data=json_to_send, format='json')
        self.assertEqual(response.status_code, self.status_OK)
        response_json = response.json()
        self.assertEqual(self.details_traffic_limit, response_json['details'])
        self.assertEqual(traffic_limit_in_mb, response_json[self.data_key_name][0]['traffic_limit'] / 1024 / 1024)

    def test_vpn_token_patch_valid_until_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        days = 365
        new_date = (datetime.datetime.now() + datetime.timedelta(days=days)).strftime(DATE_STRING_FORMAT)
        json_to_send = {
            'token_id': self.vpn_token.id,
            'valid_until': days
        }
        self.assertIsNone(self.vpn_token.valid_until)
        response = self.client.patch(self.url, data=json_to_send, format='json')
        self.assertEqual(response.status_code, self.status_OK)
        response_json = response.json()
        self.assertEqual(self.details_valid_until, response_json['details'])
        self.assertEqual(new_date, response_json[self.data_key_name][0]['valid_until'])

    @patch("requests.delete", return_value=mocks.MockResponseStatusCode204())
    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_vpn_token_patch_else_ok(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        json_to_send = {
            'token_id': self.vpn_token.id,
        }
        self.vpn_token.traffic_limit = 1024
        self.vpn_token.save()
        response = self.client.patch(self.url, data=json_to_send, format='json')
        self.assertEqual(response.status_code, self.status_OK)
        response_json = response.json()
        self.assertEqual(self.details_else, response_json['details'])
        self.assertEqual(self.vpn_token.id, response_json[self.data_key_name][0]['id'])
        self.assertIsNone(response_json[self.data_key_name][0]['traffic_limit'])

    def test_vpn_token_patch_traffic_limit_vpn_token_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        traffic_limit_in_mb = 1024
        json_to_send = {
            'token_id': self.invalid_token_id,
            'traffic_limit': traffic_limit_in_mb
        }
        response = self.client.patch(self.url, data=json_to_send, format='json')
        self.assertEqual(response.status_code, self.status_NOT_FOUND)

    def test_vpn_token_patch_valid_until_vpn_token_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        days = 365
        json_to_send = {
            'token_id': self.invalid_token_id,
            'valid_until': days
        }
        response = self.client.patch(self.url, data=json_to_send, format='json')
        self.assertEqual(response.status_code, self.status_NOT_FOUND)

    def test_vpn_token_patch_else_vpn_token_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        json_to_send = {
            'token_id': self.invalid_token_id,
        }
        response = self.client.patch(self.url, data=json_to_send, format='json')
        self.assertEqual(response.status_code, self.status_NOT_FOUND)

    def test_vpn_token_patch_traffic_limit_vpn_server_does_not_exist(self):
        """Недостижимый сценарий, на VPN сервер foreign key из vpn_token и он заведомо существует,
        тк создать ключ без сервера невозможно"""
        pass

    def test_vpn_token_patch_else_vpn_server_does_not_exist(self):
        """Недостижимый сценарий, на VPN сервер foreign key из vpn_token и он заведомо существует,
        тк создать ключ без сервера невозможно"""
        pass

    @patch("requests.put", return_value=mocks.MockResponseStatusCode404())
    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_vpn_token_patch_traffic_limit_vpn_server_response_error(self, *args):
        traffic_limit_in_mb = 1024
        json_to_send = {
            'token_id': self.vpn_token.id,
            'traffic_limit': traffic_limit_in_mb
        }
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        response = self.client.patch(self.url, data=json_to_send, format='json')
        self.assertEqual(response.status_code, self.status_SERVICE_UNAVAILABLE)

    @patch("requests.delete", return_value=mocks.MockResponseStatusCode404())
    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    def test_vpn_token_patch_else_vpn_server_response_error(self, *args):
        json_to_send = {
            'token_id': self.vpn_token.id,
        }
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        response = self.client.patch(self.url, data=json_to_send, format='json')
        self.assertEqual(response.status_code, self.status_SERVICE_UNAVAILABLE)

    @patch("requests.get", return_value=mocks.MockResponseStatusCode404())
    def test_vpn_token_patch_traffic_limit_vpn_server_does_not_response(self, *args):
        traffic_limit_in_mb = 1024
        json_to_send = {
            'token_id': self.vpn_token.id,
            'traffic_limit': traffic_limit_in_mb
        }
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        response = self.client.patch(self.url, data=json_to_send, format='json')
        self.assertEqual(response.status_code, self.status_SERVICE_UNAVAILABLE)

    @patch("requests.get", return_value=mocks.MockResponseStatusCode404())
    def test_vpn_token_patch_else_vpn_server_does_not_response(self, *args):
        json_to_send = {
            'token_id': self.vpn_token.id,
        }
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        response = self.client.patch(self.url, data=json_to_send, format='json')
        self.assertEqual(response.status_code, self.status_SERVICE_UNAVAILABLE)


class TransportTest(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('api:get_transports')
        cls.details = 'get_transports'
        cls.data_key_name = 'transports'

    def test_transport_ok(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        response = self.client.get(self.url, format='json')
        self.assertEqual(self.status_OK, response.status_code)
        json_data = response.json()
        self.assertIn(self.details, json_data['details'])
        self.assertEqual(1 + self.transport_cnt, len(json_data[self.data_key_name]))

    def test_transport_no_auth(self):
        self.client.credentials()
        response = self.client.get(self.url, format='json')
        self.assertEqual(self.status_UNAUTHORIZED, response.status_code)


class TelegramMessageSendTest(BaseAPITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('api:telegram_message_send')
        cls.details_all = 'All users message send'
        cls.details_personal = 'Personal message send'
        cls.data_key_name = 'info'
        cls.text_to_send = 'test message'

    @patch('telebot.TeleBot.send_message', return_value=mocks.MockResponseStatusCode200())
    def test_telegram_message_send_ok_personal(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        json_to_send = {
            'transport_name': self.transport_name,
            'text': self.text_to_send,
            'messenger_id': self.credentials['id'],
        }
        response = self.client.post(self.url, data=json_to_send, format='json')
        self.assertEqual(self.status_OK, response.status_code)
        json_data = response.json()
        self.assertIn(self.details_personal, json_data['details'])
        self.assertEqual(json_data[self.data_key_name]['success'], 1)
        self.assertEqual(json_data[self.data_key_name]['error'], 0)

    @patch('telebot.TeleBot.send_message', return_value=mocks.MockResponseStatusCode200())
    def test_telegram_message_send_ok_all(self, *args):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        json_to_send = {
            'transport_name': self.transport_name,
            'text': self.text_to_send,
        }
        response = self.client.post(self.url, data=json_to_send, format='json')
        self.assertEqual(self.status_OK, response.status_code)
        json_data = response.json()
        self.assertIn(self.details_all, json_data['details'])
        self.assertEqual(json_data[self.data_key_name]['success'], 1)
        self.assertEqual(json_data[self.data_key_name]['error'], 0)

    def test_telegram_message_send_no_auth(self):
        self.client.credentials()
        response = self.client.post(self.url, format='json')
        self.assertEqual(self.status_UNAUTHORIZED, response.status_code)

    def test_telegram_message_send_transport_does_not_exist(self):
        self.client.credentials(HTTP_AUTHORIZATION=self.HTTP_AUTHORIZATION)
        json_to_send = {
            'transport_name': self.not_exist_transport,
            'text': self.text_to_send,
        }
        response = self.client.post(self.url, data=json_to_send, format='json')
        self.assertEqual(self.status_NOT_FOUND, response.status_code)
        self.assertIn(f"Transport {self.not_exist_transport!r} does not exist", response.json()['details'])

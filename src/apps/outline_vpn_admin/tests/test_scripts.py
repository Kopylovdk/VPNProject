from apps.outline_vpn_admin import scripts
import apps.outline_vpn_admin.tests.mocks as mocks
import datetime
import apps.outline_vpn_admin.tests.helpers as helpers
from unittest.mock import patch
from django.test import TestCase

from apps.outline_vpn_admin.models import TokenProcess, Transport, Tariff


class BaseSetUp(TestCase):
    def setUp(self) -> None:
        self.date_now = datetime.datetime.now()
        self.clients = helpers.create_client(2)
        self.transports = []
        for i in range(1, 3):
            self.transports.append(helpers.create_transport(transport_name=f'test_{i}')[0])
        self.tariff = helpers.create_tariff(currency=helpers.create_currency()[0])[0]
        self.vpn_server_name = 'test_scripts'
        self.vpn_server = helpers.create_vpn_server(server_name=self.vpn_server_name)[0]
        self.contacts = []
        self.count = 6
        self.vpn_keys = []
        for cnt in range(self.count):
            if cnt < 3:
                creds = {"id": 3333, "first_name": "first_name_3", "last_name": "last_name_3", "phone_number": '333'}
                client = self.clients[0]
                transport = self.transports[0]
            else:
                creds = {"id": 6666, "first_name": "first_name_6", "last_name": "last_name_6", "phone_number": '666'}
                client = self.clients[1]
                transport = self.transports[1]

            if cnt in [0, 3]:
                contact = helpers.create_contact(
                    client=client,
                    transport=transport,
                    credentials=creds,
                )[0]
                self.contacts.append(contact)

            vpn_key = helpers.create_vpn_token(
                vpn_server=self.vpn_server,
                tariff=self.tariff,
                client=client
            )[0]

            if cnt in [0, 5]:
                valid_date = self.date_now + datetime.timedelta(days=2)
            elif cnt in [1, 4]:
                valid_date = self.date_now - datetime.timedelta(days=2)
            elif cnt in [2]:
                valid_date = self.date_now
            else:
                valid_date = self.date_now + datetime.timedelta(days=7)
            vpn_key.valid_until = valid_date
            vpn_key.outline_id = cnt + 1
            vpn_key.save()
            self.vpn_keys.append(vpn_key)


class CollectExpiredVPNTokenTestCase(BaseSetUp):
    def test_collect_expired_vpn_token(self):
        scripts.collect_expired_vpn_token()
        token_process = TokenProcess.objects.filter(
            is_executed=False,
            script_name=scripts.EXPIRED_VPN_TOKEN_SCRIPT_NAME,
        )
        self.assertEqual(2, len(token_process))
        self.assertFalse(token_process[0].executed_at)
        self.assertFalse(token_process[1].executed_at)


class ProcessExpiredVPNTokensTGTestCase(BaseSetUp):
    def test_process_expired_vpn_tokens_tg(self):
        pass


class TaskUpdateTestCase(BaseSetUp):
    def test_task_update(self):
        to_update = TokenProcess(
            vpn_token=self.vpn_keys[1],
            transport=self.transports[0],
            contact=self.contacts[0],
            vpn_server=self.vpn_server,
            script_name='test_task_update',
            text='test_task_update_text',
        )
        to_update.save()
        self.assertFalse(to_update.executed_at)
        self.assertFalse(to_update.is_executed)

        self.assertTrue(scripts.task_update(to_update))

        self.assertTrue(to_update.executed_at)
        self.assertTrue(to_update.is_executed)


class VPNTokenDeactivateTestCase(BaseSetUp):
    def test_vpn_token_deactivate(self):
        self.assertTrue(self.vpn_keys[1].is_active)

        self.assertTrue(scripts.vpn_token_deactivate(self.vpn_keys[1]))

        self.assertFalse(self.vpn_keys[1].is_active)
        self.assertIn('Deleted by script.', self.vpn_keys[1].name)


class OutlineTokenDeleteTestCase(BaseSetUp):
    @patch("requests.delete", return_value=mocks.MockResponseStatusCode204())
    def test_outline_token_delete_ok(self, mocked_delete):
        self.assertTrue(scripts.outline_token_delete(self.vpn_keys[0], self.vpn_server))

    @patch('requests.delete', return_value=mocks.MockResponseStatusCode404())
    def test_outline_token_delete_false(self, mocked_delete):
        self.assertFalse(scripts.outline_token_delete(self.vpn_keys[0], self.vpn_server))


class SendTelegramMessageTestCase(BaseSetUp):
    @patch('telebot.TeleBot.send_message', return_value=mocks.MockResponseStatusCode200())
    def test_send_telegram_message(self, mock):
        scripts.send_telegram_message(self.transports[0], 'text', self.contacts[0])

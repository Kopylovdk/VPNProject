import apps.outline_vpn_admin.tests.mocks as mocks
import datetime
import apps.outline_vpn_admin.tests.helpers as helpers
from apps.outline_vpn_admin.apscheduler import jobs
from apps.outline_vpn_admin.apscheduler import jobs_helpers
from unittest.mock import patch
from django.test import TestCase
from apps.outline_vpn_admin.exceptions import VPNServerDoesNotResponse
from apps.outline_vpn_admin.models import TokenProcess, Transport
from vpnservice.settings import DATE_STRING_FORMAT


class BaseSetUp(TestCase):
    def setUp(self) -> None:
        self.test_str = 'test'
        self.date_now = datetime.date.today()
        self.transports = []
        for i in range(1, 4):
            self.transports.append(helpers.create_transport(transport_name=f'{self.test_str}_{i}')[0])
        self.transports[0].name = self.transports[0].name + ' ' + jobs.tg_messanger_name
        self.transports[1].name = self.transports[1].name + ' ' + jobs.tg_messanger_name
        self.transports[0].save()
        self.transports[1].save()
        self.tariff = helpers.create_tariff(currency=helpers.create_currency()[0])[0]
        # self.vpn_server_name = 'test_scripts'
        self.vpn_server = helpers.create_vpn_server(server_name=f'{self.test_str}_server_scripts')[0]
        self.contacts = []
        self.count = 6
        self.vpn_keys = []
        self.clients = helpers.create_client(2)
        for cnt in range(self.count):
            if cnt in [0, 1, 2]:
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
            if cnt == 1:
                contact = helpers.create_contact(
                    client=client,
                    transport=self.transports[1],
                    credentials=creds,
                )[0]
                self.contacts.append(contact)
            if cnt == 4:
                contact = helpers.create_contact(
                    client=client,
                    transport=self.transports[2],
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
        self.token_processes = []
        for cnt in range(self.count):
            if cnt in [0, 1, 2]:
                script_name = jobs.EXPIRED_VPN_TOKEN_SCRIPT_NAME
                transport = self.transports[0]
                contact = self.contacts[0]
            else:
                script_name = jobs.INFORM_BEFORE_EXPIRED_VPN_TOKEN_SCRIPT_NAME
                transport = self.transports[0]
                contact = self.contacts[1]
            token_process = TokenProcess(
                vpn_token=self.vpn_keys[cnt],
                transport=transport,
                contact=contact,
                vpn_server=self.vpn_server,
                script_name=script_name,
                text=f'{self.test_str}_set_up_token_process_text',
            )
            token_process.save()
            self.token_processes.append(token_process)


class CollectActiveTokensTestCase(BaseSetUp):
    def test_collect_active_tokens(self):
        tokens = jobs_helpers.collect_active_tokens()
        self.assertEqual(len(self.vpn_keys), tokens.count())


class CollectActiveClientTransportsTestCase(BaseSetUp):
    def test_collect_active_client_transports(self):
        exist_client_transport_in_migration = 1
        transports = jobs_helpers.collect_active_client_transports()
        self.assertEqual(
            len(self.transports) + exist_client_transport_in_migration,
            transports.count()
        )


class CreateExpiredVPNTokenTestCase(BaseSetUp):
    def test_create_expired_vpn_token_task(self):
        jobs.create_expired_vpn_token_task()
        token_process = TokenProcess.objects.filter(
            is_executed=False,
            script_name=jobs.EXPIRED_VPN_TOKEN_SCRIPT_NAME,
        ).exclude(text='test_set_up_token_process_text')
        self.assertEqual(4, len(token_process))
        self.assertFalse(token_process[0].executed_at)
        self.assertFalse(token_process[1].executed_at)
        self.assertFalse(token_process[2].executed_at)
        self.assertFalse(token_process[3].executed_at)


class CreateBeforeExpireTasksTestCase(BaseSetUp):
    @patch('telebot.TeleBot.send_message', return_value=mocks.MockResponseStatusCode200())
    def test_create_before_expired_user_inform_tasks(self, *args):
        jobs.create_before_expired_user_inform_tasks()
        self.assertEqual(len(self.token_processes) + 2, TokenProcess.objects.count())


class CreateProcessTasksTestCase(BaseSetUp):
    def test_create_process_tasks(self):
        transports = Transport.objects.filter(is_active=True, is_admin_transport=False)
        jobs_helpers.create_process_tasks(
            vpn_token=self.vpn_keys[0],
            text=self.test_str,
            script_name=self.test_str,
            transports=transports,
        )
        self.assertEqual(TokenProcess.objects.filter(script_name=self.test_str).count(), 2)


class ProcessInformTasksTGTestCase(BaseSetUp):
    @patch('telebot.TeleBot.send_message', return_value=mocks.MockResponseStatusCode200())
    def test_process_inform_tasks_tg(self, *args):
        jobs.process_inform_tasks_tg()
        token_processes_execute = TokenProcess.objects.filter(is_executed=True)
        self.assertEqual(token_processes_execute.count(), 3)
        self.assertEqual(token_processes_execute[0].script_name, jobs.INFORM_BEFORE_EXPIRED_VPN_TOKEN_SCRIPT_NAME)
        self.assertTrue(token_processes_execute[0].is_executed)
        self.assertIsNotNone(token_processes_execute[0].executed_at)
        self.assertEqual(token_processes_execute[1].script_name, jobs.INFORM_BEFORE_EXPIRED_VPN_TOKEN_SCRIPT_NAME)
        self.assertTrue(token_processes_execute[1].is_executed)
        self.assertIsNotNone(token_processes_execute[1].executed_at)
        self.assertEqual(token_processes_execute[2].script_name, jobs.INFORM_BEFORE_EXPIRED_VPN_TOKEN_SCRIPT_NAME)
        self.assertTrue(token_processes_execute[2].is_executed)
        self.assertIsNotNone(token_processes_execute[2].executed_at)


class ProcessExpiredVPNTokensTGTestCase(BaseSetUp):
    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    @patch("requests.delete", return_value=mocks.MockResponseStatusCode204())
    @patch('telebot.TeleBot.send_message', return_value=mocks.MockResponseStatusCode200())
    def test_process_expired_vpn_tokens_tg(self, *args):
        self.assertEqual(len(self.token_processes), self.count)
        jobs.process_expired_vpn_tokens_tg()
        token_processes_execute = TokenProcess.objects.filter(is_executed=True)
        self.assertEqual(token_processes_execute.count(), 3)
        self.assertEqual(token_processes_execute[0].script_name, jobs.EXPIRED_VPN_TOKEN_SCRIPT_NAME)
        self.assertTrue(token_processes_execute[0].is_executed)
        self.assertIsNotNone(token_processes_execute[0].executed_at)
        self.assertEqual(token_processes_execute[1].script_name, jobs.EXPIRED_VPN_TOKEN_SCRIPT_NAME)
        self.assertTrue(token_processes_execute[1].is_executed)
        self.assertIsNotNone(token_processes_execute[1].executed_at)
        self.assertEqual(token_processes_execute[2].script_name, jobs.EXPIRED_VPN_TOKEN_SCRIPT_NAME)
        self.assertTrue(token_processes_execute[2].is_executed)
        self.assertIsNotNone(token_processes_execute[2].executed_at)


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

        jobs_helpers.task_update(to_update)

        self.assertTrue(to_update.executed_at)
        self.assertTrue(to_update.is_executed)


class VPNTokenDeactivateTestCase(BaseSetUp):
    def test_vpn_token_deactivate_ok(self):
        self.assertTrue(self.vpn_keys[1].is_active)

        jobs_helpers.vpn_token_deactivate(self.vpn_keys[1])

        self.assertFalse(self.vpn_keys[1].is_active)
        self.assertIn('Deleted by script.', self.vpn_keys[1].name)


class OutlineTokenDeleteTestCase(BaseSetUp):
    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    @patch("requests.delete", return_value=mocks.MockResponseStatusCode204())
    def test_outline_token_delete_ok(self, *args):
        jobs_helpers.outline_token_delete(self.vpn_keys[0], self.vpn_server)

    @patch("requests.get", return_value=mocks.MockResponseGetServerInfo())
    @patch('requests.delete', return_value=mocks.MockResponseStatusCode404())
    def test_outline_token_delete_false(self, *args):
        with self.assertRaises(VPNServerDoesNotResponse):
            jobs_helpers.outline_token_delete(self.vpn_keys[0], self.vpn_server)


class SendTelegramMessageTestCase(BaseSetUp):
    @patch('telebot.TeleBot.send_message', return_value=mocks.MockResponseStatusCode200())
    def test_send_telegram_message(self, *args):
        jobs_helpers.send_telegram_message(self.transports[0], 'text', self.contacts[0])




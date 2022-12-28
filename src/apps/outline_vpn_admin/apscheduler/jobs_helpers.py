import logging
import datetime
from django.db.models import QuerySet
from telebot.apihelper import ApiHTTPException
from apps.outline_vpn_admin import exceptions
from telebot import TeleBot
from apps.outline_vpn_admin.outline_api import get_outline_client
from apps.outline_vpn_admin.models import (
    TokenProcess,
    Contact,
    Transport,
    VPNToken,
    VPNServer,
)


log = logging.getLogger(__name__)


def collect_active_tokens():
    return VPNToken.objects.select_related('tariff', 'server', 'client').filter(is_active=True)


def collect_active_client_transports():
    return Transport.objects.filter(is_active=True, is_admin_transport=False)


def create_process_tasks(vpn_token: VPNToken, text: str, script_name: str, transports: QuerySet[Transport]):
    for transport in transports:
        contacts = vpn_token.client.contact_set.filter(transport=transport)
        if contacts.count() == 0:
            log.info(
                f"VPN Token: {vpn_token.as_dict()},"
                f" client {vpn_token.client.as_dict()!r}"
                f" don't have contact with transport {transport.name!r}"
            )
            continue
        for contact in contacts:
            process = TokenProcess.objects.create(
                vpn_token=vpn_token,
                transport=transport,
                script_name=script_name,
                contact=contact,
                vpn_server=vpn_token.server,
                text=text,
            )
            process.save()


def task_update(task: TokenProcess) -> None:
    task.executed_at = datetime.datetime.now()
    task.is_executed = True
    try:
        task.save()
    except Exception as err:
        log.error(f'{task.as_dict()!r} save to database error={err}')
        raise exceptions.ProcessException


def vpn_token_deactivate(token: VPNToken) -> None:
    token.is_active = False
    token.last_inform_date = datetime.datetime.now()
    token.name = f'Deleted by script. {token.name}'
    try:
        token.save()
    except Exception as err:
        log.error(f'{token.as_dict()!r} save to database error={err}')
        raise exceptions.ProcessException


def outline_token_delete(token: VPNToken, server: VPNServer) -> None:
    outline_client = get_outline_client(server)
    if not outline_client.delete_key(token.outline_id):
        msg = 'Outline client error occurred due outline_token_delete'
        log.error(f'{msg}')
        raise exceptions.VPNServerDoesNotResponse


def send_telegram_message(transport: Transport, text: str, contact: Contact) -> None:
    bot = TeleBot(transport.credentials['token'])
    try:
        bot.send_message(contact.credentials['id'], text)
    except ApiHTTPException as err:
        log.error(f'send_telegram_message by script {err=!r}')

import datetime
import logging
from apps.outline_vpn_admin.models import (
    TokenProcess,
    Contact,
    Transport,
    VPNToken,
    VPNServer,
)
from apps.outline_vpn_admin.outline_api import get_outline_client
from telebot import TeleBot


log = logging.getLogger(__name__)
EXPIRED_VPN_TOKEN_SCRIPT_NAME = 'expired_vpn_token_key'


def collect_expired_vpn_token():
    transports = Transport.objects.all()
    active_tokens = VPNToken.objects.select_related('tariff', 'server', 'client').filter(is_active=True)
    for transport in transports:
        to_deactivate = active_tokens.filter(transport=transport, valid_until__gte=datetime.datetime.now())
        for vpn_token in to_deactivate:
            contact = vpn_token.client.contact_set.get(transport=transport)
            text = f'Срок действия VPN ключа с ID={vpn_token.id} по тарифу {vpn_token.tariff.name} истек.\n' \
                   f'Спасибо, что воспользовались нашим VPN.\n'
            process = TokenProcess.objects.create(
                vpn_token=vpn_token,
                transport=transport,
                script_name=EXPIRED_VPN_TOKEN_SCRIPT_NAME,
                contact=contact,
                vpn_server=vpn_token.server,
                text=text,
            )
            process.save()


def process_expired_vpn_tokens_tg():
    tasks = TokenProcess.objects.select_related('vpn_token', 'transport', 'contact', 'vpn_server')
    tasks = tasks.filter(script_name=EXPIRED_VPN_TOKEN_SCRIPT_NAME, is_executed=False)
    for task in tasks:
        outline_token_delete(token=task.vpn_token, server=task.vpn_server)
        vpn_token_deactivate(token=task.vpn_token)
        send_telegram_message(transport=task.transport, contact=task.contact, text=task.text)
        task_update(task=task)


def task_update(task: TokenProcess):
    task.executed_at = datetime.datetime.now()
    task.is_executed = True
    task.save()


def vpn_token_deactivate(token: VPNToken):
    token.is_active = False
    token.name = f'Deleted by script. {token.name}'
    try:
        token.save()
    except Exception as err:
        log.error(f'{token.as_dict()!r} save to database error={err}')


def outline_token_delete(token: VPNToken, server: VPNServer):
    outline_client = get_outline_client(server.name)
    if not outline_client.delete_key(token.outline_id):
        log.error('Outline client error occurred due outline_token_delete')


def send_telegram_message(transport: Transport, text: str, contact: Contact):
    bot = TeleBot(transport.credentials['token'])
    try:
        bot.send_message(contact.credentials['id'], text)
    except Exception as err:
        log.error(f'send_telegram_message by script {err=!r}')

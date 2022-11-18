import datetime
import logging
from django_apscheduler.jobstores import DjangoJobStore
from telebot import TeleBot
from apscheduler.schedulers.blocking import BlockingScheduler
from apps.outline_vpn_admin.models import (
    TokenProcess,
    Contact,
    Transport,
    VPNToken,
    VPNServer,
)
from apps.outline_vpn_admin.outline_api import get_outline_client
from django.db import transaction
from vpnservice import settings
#TODO: create tests

log = logging.getLogger(__name__)
EXPIRED_VPN_TOKEN_SCRIPT_NAME = 'expired_vpn_token_key'


scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
scheduler.add_jobstore(DjangoJobStore(), 'expired_vpn_tokens')


@scheduler.scheduled_job(
    trigger='cron',
    day_of_week='mon-fri',
    jobstore='expired_vpn_tokens',
    id='collect_expired_vpn_token',
)
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


@scheduler.scheduled_job(
    trigger='interval',
    minutes=1,
    jobstore='expired_vpn_tokens',
    id='process_expired_vpn_tokens_tg',
)
def process_expired_vpn_tokens_tg():
    tasks = TokenProcess.objects.select_related('vpn_token', 'transport', 'contact', 'vpn_server')
    tasks = tasks.filter(script_name=EXPIRED_VPN_TOKEN_SCRIPT_NAME, is_executed=False)
    for task in tasks:
        with transaction.atomic():
            token_delete_result = outline_token_delete(token=task.vpn_token, server=task.vpn_server)
            token_deactivate_result = vpn_token_deactivate(token=task.vpn_token)
            task_update(task)
            if not token_deactivate_result and not token_delete_result:
                raise
        send_telegram_message(transport=task.transport, contact=task.contact, text=task.text)


def task_update(task: TokenProcess) -> bool:
    task.executed_at = datetime.datetime.now()
    task.is_executed = True
    try:
        task.save()
    except Exception as err:
        log.error(f'{task.as_dict()!r} save to database error={err}')
        return False
    return True


def vpn_token_deactivate(token: VPNToken):
    token.is_active = False
    token.name = f'Deleted by script. {token.name}'
    try:
        token.save()
    except Exception as err:
        log.error(f'{token.as_dict()!r} save to database error={err}')
        return False
    return True


def outline_token_delete(token: VPNToken, server: VPNServer) -> bool:
    outline_client = get_outline_client(server.name)
    if not outline_client.delete_key(token.outline_id):
        log.error('Outline client error occurred due outline_token_delete')
        return False
    return True


def send_telegram_message(transport: Transport, text: str, contact: Contact):
    bot = TeleBot(transport.credentials['token'])
    try:
        bot.send_message(contact.credentials['id'], text)
    except Exception as err:
        log.error(f'send_telegram_message by script {err=!r}')


def start_scheduler():
    scheduler.start()

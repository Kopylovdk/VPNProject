import datetime
import logging

from telebot.apihelper import ApiHTTPException

from apps.outline_vpn_admin import exceptions
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

log = logging.getLogger(__name__)
EXPIRED_VPN_TOKEN_SCRIPT_NAME = 'expired_vpn_token_key'
tg_messanger_name = 'telegram'
scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
scheduler.add_jobstore(DjangoJobStore(), 'expired_vpn_tokens')


@scheduler.scheduled_job(
    trigger='cron',
    day_of_week='1-6',
    hour=1,
    minute=0,
    second=0,
    jobstore='expired_vpn_tokens',
    id='collect_expired_vpn_token',
)
def collect_expired_vpn_token():
    transports = Transport.objects.filter(is_active=True, is_admin_transport=False)
    date = datetime.datetime.now()
    active_tokens = VPNToken.objects.select_related('tariff', 'server', 'client').filter(
        is_active=True,
        valid_until__lt=date,
    )
    for vpn_token in active_tokens:
        for transport in transports:
            contacts = vpn_token.client.contact_set.filter(transport=transport)
            if contacts.count() == 0:
                log.info(
                    f"VPN Token: {vpn_token.as_dict()},"
                    f" client {vpn_token.client.as_dict()!r}"
                    f" don't have contact with transport {transport.as_dict()!r}"
                )
                continue
            for contact in contacts:
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
        if tg_messanger_name in task.transport.name:
            with transaction.atomic():
                if task.vpn_token.is_active:
                    outline_token_delete(token=task.vpn_token, server=task.vpn_server)
                    vpn_token_deactivate(token=task.vpn_token)
                task_update(task)
                send_telegram_message(transport=task.transport, contact=task.contact, text=task.text)


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


def start_scheduler():
    scheduler.start()

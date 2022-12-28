import datetime
import logging
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from apps.outline_vpn_admin.models import TokenProcess
from django.db import transaction
from vpnservice import settings
from apps.outline_vpn_admin.apscheduler.jobs_helpers import (
    collect_active_tokens,
    collect_active_client_transports,
    create_process_tasks,
    send_telegram_message,
    task_update,
    outline_token_delete,
    vpn_token_deactivate,
    collect_active_vpn_servers,
    get_traffic_usage_on_vpn_server,
)
log = logging.getLogger(__name__)
EXPIRED_VPN_TOKEN_SCRIPT_NAME = 'expired_vpn_token_key'
INFORM_BEFORE_EXPIRED_VPN_TOKEN_SCRIPT_NAME = 'inform_before_vpn_token_key_expired'
JOB_STORE_EXPIRED_VPN_TOKENS_NAME = 'expired_vpn_tokens'
JOB_STORE_UPDATE_TRAFFIC_USAGE = 'update_traffic_usage'
JOB_STORE_INFORM_CLIENTS_BEFORE_EXPIRE_NAME = 'inform_clients_before_expire_vpn_token'
tg_messanger_name = 'telegram'

scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
scheduler.add_jobstore(DjangoJobStore(), JOB_STORE_EXPIRED_VPN_TOKENS_NAME)
scheduler.add_jobstore(DjangoJobStore(), JOB_STORE_INFORM_CLIENTS_BEFORE_EXPIRE_NAME)
scheduler.add_jobstore(DjangoJobStore(), JOB_STORE_UPDATE_TRAFFIC_USAGE)


@scheduler.scheduled_job(
    trigger='cron',
    day_of_week='0-6',
    hour=1,
    minute=0,
    second=0,
    jobstore=JOB_STORE_EXPIRED_VPN_TOKENS_NAME,
    id='create_expired_vpn_token_task',
)
def create_expired_vpn_token_task():
    date = datetime.date.today()
    vpn_tokens_to_expire = collect_active_tokens().filter(valid_until__lt=date)
    transports = collect_active_client_transports()
    for vpn_token in vpn_tokens_to_expire:
        text = f'Срок действия VPN ключа с ID={vpn_token.id} по тарифу {vpn_token.tariff.name} истек.\n' \
               f'Спасибо, что воспользовались нашим VPN.\n'
        create_process_tasks(
            vpn_token=vpn_token,
            text=text,
            script_name=EXPIRED_VPN_TOKEN_SCRIPT_NAME,
            transports=transports,
        )


@scheduler.scheduled_job(
    trigger='cron',
    day_of_week='0-6',
    hour=1,
    minute=10,
    second=0,
    jobstore=JOB_STORE_INFORM_CLIENTS_BEFORE_EXPIRE_NAME,
    id='create_before_expired_user_inform_task',
)
def create_before_expired_user_inform_tasks():
    days_before_expire = [30, 14, 7, 1]
    date = datetime.date.today()
    active_vpn_tokens = collect_active_tokens()
    transports = collect_active_client_transports()
    for days in days_before_expire:
        tokens_expired_in_ = active_vpn_tokens.filter(
            valid_until=date + datetime.timedelta(days=days),
        )
        for vpn_token in tokens_expired_in_:
            text = f'Срок действия VPN ключа с ID={vpn_token.id} по тарифу {vpn_token.tariff.name} ' \
                   f'истекает через {days} дней.\n'
            create_process_tasks(
                vpn_token=vpn_token,
                text=text,
                script_name=INFORM_BEFORE_EXPIRED_VPN_TOKEN_SCRIPT_NAME,
                transports=transports
            )


@scheduler.scheduled_job(
    trigger='interval',
    minutes=1,
    jobstore=JOB_STORE_INFORM_CLIENTS_BEFORE_EXPIRE_NAME,
    id='process_inform_tasks_tg',
)
def process_inform_tasks_tg():
    tasks = TokenProcess.objects.select_related('vpn_token', 'transport', 'contact', 'vpn_server')
    tasks = tasks.filter(script_name=INFORM_BEFORE_EXPIRED_VPN_TOKEN_SCRIPT_NAME, is_executed=False)
    for task in tasks:
        if tg_messanger_name in task.transport.name:
            with transaction.atomic():
                send_telegram_message(transport=task.transport, contact=task.contact, text=task.text)
                task_update(task)


@scheduler.scheduled_job(
    trigger='interval',
    minutes=1,
    jobstore=JOB_STORE_EXPIRED_VPN_TOKENS_NAME,
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


@scheduler.scheduled_job(
    trigger='interval',
    minutes=20,
    jobstore=JOB_STORE_UPDATE_TRAFFIC_USAGE,
    id='update_vpn_token_traffic_usage',
)
def update_vpn_token_traffic_usage():
    vpn_tokens = collect_active_tokens()
    vpn_servers = collect_active_vpn_servers()
    for vpn_server in vpn_servers:
        tokens_to_update_traffic_usage = vpn_tokens.filter(server=vpn_server, traffic_limit__gt=0)
        traffic_usage = get_traffic_usage_on_vpn_server(vpn_server)
        for vpn_token in tokens_to_update_traffic_usage:
            vpn_token.traffic_used = traffic_usage.get(str(vpn_token.outline_id))
            vpn_token.traffic_last_update = datetime.datetime.now()
            vpn_token.save()


def start_scheduler():
    scheduler.start()

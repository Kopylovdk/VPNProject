import logging
from django.conf import settings
from apscheduler.schedulers.blocking import BlockingScheduler
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.triggers.cron import CronTrigger
from apps.outline_vpn_admin.scripts_vpnkeys import expire_vpn_key, expired_soon_vpn_keys


logger = logging.getLogger(__name__)


def add_tasks_and_start():
    scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(), "default")

    scheduler.add_job(
        expire_vpn_key,
        trigger=CronTrigger(hour=1, minute=0),
        id='expire_vpn_keys',
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'expire_vpn_keys'.")

    scheduler.add_job(
        expired_soon_vpn_keys,
        trigger=CronTrigger(hour=1, minute=30),
        id='expired_soon_vpn_keys',
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job 'expired_soon_vpn_keys'.")

    try:
        logger.info("Starting scheduler...")
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully!")

import threading
from django.core.management.base import BaseCommand
from apps.outline_vpn_admin.apscheduler.jobs import start_scheduler


class Command(BaseCommand):
    help = 'Process expired vpn token and send msg to users'

    def handle(self, *args, **options):
        threading.Thread(start_scheduler(), name='process_expired_keys_thread')

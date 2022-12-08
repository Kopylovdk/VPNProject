import threading
from django.core.management.base import BaseCommand
from apps.outline_vpn_admin.scripts import collect_expired_vpn_token


class Command(BaseCommand):
    help = 'Collect expired vpn token and save them to TokenProcess model'

    def handle(self, *args, **options):
        threading.Thread(collect_expired_vpn_token(), name='collect_expired_keys_thread')

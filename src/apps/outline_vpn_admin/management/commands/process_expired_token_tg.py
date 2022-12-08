import threading
from django.core.management.base import BaseCommand
from apps.outline_vpn_admin.scripts import process_expired_vpn_tokens_tg


class Command(BaseCommand):
    help = 'Process expired vpn token and send msg to users'

    def handle(self, *args, **options):
        threading.Thread(process_expired_vpn_tokens_tg(), name='process_expired_keys_thread')

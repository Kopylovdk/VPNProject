import threading
from django.core.management.base import BaseCommand
from apps.service.script_vpnkeys_expired import expire_vpn_key


class Command(BaseCommand):
    def handle(self, *args, **options):
        threading.Thread(expire_vpn_key(), name='expired_keys_thread')

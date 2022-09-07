import threading
from django.core.management.base import BaseCommand
from apps.outline_vpn_admin.scripts_vpnkeys import expire_vpn_key


class Command(BaseCommand):
    help = 'For manual use for expire_vpn_key'

    def handle(self, *args, **options):
        threading.Thread(expire_vpn_key(), name='expired_keys_thread')

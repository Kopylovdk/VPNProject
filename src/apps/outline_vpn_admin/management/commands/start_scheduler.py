from django.core.management.base import BaseCommand
from apps.outline_vpn_admin.scheduler import add_tasks_and_start


class Command(BaseCommand):
    def handle(self, *args, **options):
        add_tasks_and_start()

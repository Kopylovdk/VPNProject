from django.core.management.base import BaseCommand
from apps.service.scheduler import add_tasks_and_start


class Command(BaseCommand):
    def handle(self, *args, **options):
        add_tasks_and_start()

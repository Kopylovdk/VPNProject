import threading
from django.core.management.base import BaseCommand
from apps.service.bot.bot_main import bot


class Command(BaseCommand):
    def handle(self, *args, **options):
        threading.Thread(bot.polling(none_stop=True, interval=0), name='telegram_thread')

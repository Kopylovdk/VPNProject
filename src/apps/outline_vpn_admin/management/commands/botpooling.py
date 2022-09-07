from django.core.management.base import BaseCommand
from outline_vpn_admin_bot.bot_main import bot


class Command(BaseCommand):
    def handle(self, *args, **options):
        bot.polling(none_stop=True, interval=0)

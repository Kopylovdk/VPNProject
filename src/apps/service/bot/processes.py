from apps.service.models import TelegramUsers
from telebot.types import User


def add_new_tg_user(telegram_user: User) -> None:
    if not TelegramUsers.objects.filter(telegram_id=telegram_user.id):
        new_record = TelegramUsers(
            telegram_id=telegram_user.id,
            telegram_login=telegram_user.username,
            telegram_first_name=telegram_user.first_name,
            telegram_last_name=telegram_user.last_name,
        )
        new_record.save()


def add_new_vpn_key_to_tg_user():
    pass
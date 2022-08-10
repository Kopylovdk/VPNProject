from apps.service.models import VPNServiceRecord
from telebot.types import User


def add_new_tg_user(telegram_user: User) -> None:
    if not VPNServiceRecord.objects.filter(telegram_id=telegram_user.id):
        new_record = VPNServiceRecord(
            telegram_id=telegram_user.id,
            telegram_login=telegram_user.username,
            telegram_first_name=telegram_user.first_name,
            telegram_last_name=telegram_user.last_name,
        )
        new_record.save()

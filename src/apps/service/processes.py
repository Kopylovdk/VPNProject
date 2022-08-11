import datetime
from apps.service.models import TelegramUsers, OutlineVPNKeys
from telebot.types import User
import apps.service.exceptions as exceptions
from apps.service.outline.outline_api import keys_list
import logging


log = logging.getLogger(__name__)


def get_outline_key_by_id(outline_key_id: int) -> OutlineVPNKeys or None:
    try:
        return OutlineVPNKeys.objects.get(outline_key_id=outline_key_id)
    except OutlineVPNKeys.DoesNotExist:
        return


def get_tg_user_by_(telegram_login: str = None, telegram_id: int = None) -> TelegramUsers or None:
    try:
        if telegram_login:
            return TelegramUsers.objects.get(telegram_login=telegram_login)
        elif telegram_id:
            return TelegramUsers.objects.get(telegram_id=telegram_id)
    except TelegramUsers.DoesNotExist:
        return


def get_all_admins() -> list[int]:
    """
    Функция получения Telegram_id ВСЕХ администраторов
    Params: None
    Returns: None
    Exceptions: list[int]
    """
    return list(TelegramUsers.objects.filter(is_admin=True).values_list('telegram_id', flat=True))


def add_new_tg_user(telegram_user: User) -> None:
    """
    Функция добавления нового пользователя
    Params:
        telegram_user: User
    Returns: None
    Exceptions:
        exceptions.ProcessException
    """
    try:
        if not TelegramUsers.objects.filter(telegram_id=telegram_user.id):
            new_record = TelegramUsers(
                telegram_id=telegram_user.id,
                telegram_login=telegram_user.username,
                telegram_first_name=telegram_user.first_name,
                telegram_last_name=telegram_user.last_name,
            )
            new_record.save()
    except Exception as error:
        raise exceptions.ProcessException(f'Ошибка записи строки в БД: {error!r}')


def add_new_vpn_key_to_tg_user(vpn_key_id: int, user_id: int) -> None:
    key_value = ''
    keys = keys_list()

    for key in keys:
        if int(key.key_id) == vpn_key_id:
            key_value = key.access_url
            break

    new_record = OutlineVPNKeys(
        telegram_user_record=TelegramUsers.objects.get(id=user_id),
        outline_key_id=vpn_key_id,
        outline_key_value=key_value,
        outline_key_valid_until=datetime.datetime.today()
    )
    new_record.save()
    # TODO: ограничение трафика у нового ключа


def get_all_vpn_keys_of_user(user: User) -> list:
    vpn_keys = OutlineVPNKeys.objects.filter(telegram_user_record__telegram_id=user.id)
    if vpn_keys:
        return [
            f'Ключ: "{vpn_key.outline_key_value}" действует до: {vpn_key.outline_key_valid_until}' for vpn_key in vpn_keys
        ]
    else:
        return []

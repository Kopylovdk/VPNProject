import datetime
import apps.service.exceptions as exceptions
import logging
from apps.service.models import TelegramUsers, OutlineVPNKeys
from telebot.types import User
from apps.service.outline.outline_api import create_new_vpn_key
from apps.service.bot.bot_exceptions import OUTLINE_VPN_KEY_NOT_FOUND, TELEGRAM_USER_NOT_FOUND, NOT_INTEGER

log = logging.getLogger(__name__)


def _validate_int(data: str) -> int or bool:
    """
    Валидация. Является ли полученная строка числом
    Params:
        data: str
    Returns: bool
    Exceptions: None
    """
    try:
        return int(data)
    except ValueError:
        return False


def get_outline_key_by_id(telegram_data: int or str) -> OutlineVPNKeys or str:
    """
    Функция получения конкретного OutlineVPNKeys
    Params:
        outline_key_id: int
    Returns:
        OutlineVPNKeys or None
    Exceptions:
        OUTLINE_VPN_KEY_NOT_FOUND
        NOT_INTEGER
    """
    valid_data = _validate_int(telegram_data)
    try:
        if valid_data:
            return OutlineVPNKeys.objects.get(outline_key_id=valid_data)
    except OutlineVPNKeys.DoesNotExist:
        return OUTLINE_VPN_KEY_NOT_FOUND
    else:
        return NOT_INTEGER


def get_tg_user_by_(telegram_data: str or int) -> TelegramUsers or str:
    """
    Функция получения конкретного TelegramUsers
    Params:
        telegram_login: str = None
        telegram_id: int = None
    Returns:
        TelegramUsers or None
    Exceptions:
        TELEGRAM_USER_NOT_FOUND
    """

    valid_data = _validate_int(telegram_data)
    try:
        if valid_data:
            return TelegramUsers.objects.get(telegram_id=telegram_data)
        else:
            return TelegramUsers.objects.get(telegram_login=telegram_data)
    except TelegramUsers.DoesNotExist:
        return TELEGRAM_USER_NOT_FOUND


def get_all_admins() -> list[int]:
    """
    Функция получения Telegram_id ВСЕХ администраторов
    Params: None
    Returns:
        list[int]
    Exceptions: None
    """
    return list(TelegramUsers.objects.filter(is_admin=True).values_list('telegram_id', flat=True))


def get_all_no_admin_users() -> list[int]:
    """
    Функция получения Telegram_id ВСЕХ обычных пользователей
    Params: None
    Returns: list[int]
    Exceptions: None
    """
    return list(TelegramUsers.objects.filter(is_admin=False).values_list('telegram_id', flat=True))


def add_new_tg_user(user: User) -> None:
    """
    Функция добавления нового пользователя
    Params:
        telegram_user: User
    Returns: None
    Exceptions:
        exceptions.ProcessException
    """
    try:
        if not TelegramUsers.objects.filter(telegram_id=user.id):
            new_record = TelegramUsers(
                telegram_id=user.id,
                telegram_login=user.username,
                telegram_first_name=user.first_name,
                telegram_last_name=user.last_name,
            )
            new_record.save()
    except Exception as error:
        raise exceptions.ProcessException(f'Ошибка записи строки в БД: {error!r}')


def add_new_key() -> OutlineVPNKeys:
    response = create_new_vpn_key()
    vpn_key = OutlineVPNKeys(
        outline_key_id=response.key_id,
        outline_key_name=response.name,
        outline_key_value=response.access_url,
    )
    vpn_key.save()
    return vpn_key


def get_all_vpn_keys_of_user(user_data: str or int) -> list or str:
    """
    Функция получения всех VPN ключей конкретного пользователя
    Params:
        userid: int
    Returns: list
    Exceptions: None
    """
    tg_user = get_tg_user_by_(telegram_data=user_data)
    if isinstance(tg_user, TelegramUsers):
        vpn_keys = \
            OutlineVPNKeys.objects.select_related('telegram_user_record').filter(telegram_user_record=tg_user.id)
        if vpn_keys:
            to_return = []
            for vpn_key in vpn_keys:
                vpn_key_date = vpn_key.outline_key_valid_until
                if vpn_key_date:
                    vpn_key_date = f'Срок действия до: {vpn_key_date.strftime("%d-%m-%Y")!r}'
                else:
                    vpn_key_date = 'Срок действия без ограничений'\
                        if not vpn_key.outline_key_traffic_limit else 'Демо ключ на 1 гб траффика'

                to_return.append(f'ID: {vpn_key.outline_key_id!r} '
                                 f'Ключ: {vpn_key.outline_key_value!r} '
                                 f'{vpn_key_date}')
            return to_return
        else:
            return []
    else:
        return tg_user

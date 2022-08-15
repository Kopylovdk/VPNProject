import datetime
from apps.service.models import TelegramUsers, OutlineVPNKeys
from telebot.types import User
import apps.service.exceptions as exceptions
from apps.service.outline.outline_api import keys_list, del_traffic_limit, add_traffic_limit
import logging


log = logging.getLogger(__name__)


def get_outline_key_by_id(outline_key_id: int) -> OutlineVPNKeys or None:
    """
    Функция получения конкретного OutlineVPNKeys
    Params:
        outline_key_id: int
    Returns:
        OutlineVPNKeys or None
    Exceptions: None
    """
    try:
        return OutlineVPNKeys.objects.get(outline_key_id=outline_key_id)
    except OutlineVPNKeys.DoesNotExist:
        return


def get_tg_user_by_(telegram_login: str = None, telegram_id: int = None) -> TelegramUsers or None:
    """
    Функция получения конкретного TelegramUsers
    Params:
        telegram_login: str = None
        telegram_id: int = None
    Returns:
        TelegramUsers or None
    Exceptions: None
    """
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
    Returns:
        list[int]
    Exceptions: None
    """
    return list(TelegramUsers.objects.filter(is_admin=True).values_list('telegram_id', flat=True))


def get_all_no_admin_users() -> list[int]:
    """
    Функция получения Telegram_id ВСЕХ обычных пользователей
    Params: None
    Returns: None
    Exceptions: list[int]
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


def add_new_vpn_key_to_tg_user(
        vpn_key_id: int,
        tg_user: TelegramUsers,
        test: bool = False
) -> None:
    """
    Функция добавления новой записи в OutlineVPNKeys
    Params:
        vpn_key_id: int,
        tg_user: TelegramUsers,
        test: bool = False - используется для Мока обращения к реальному outline серверу
    Returns: None
    Exceptions: None
    """
    if not test:
        key_value = ''
        keys = keys_list()
        for key in keys:
            if int(key.key_id) == vpn_key_id:
                key_value = key.access_url
                break
    else:
        key_value = 'test'

    new_record = OutlineVPNKeys(
        telegram_user_record=tg_user,
        outline_key_id=vpn_key_id,
        outline_key_value=key_value,
        outline_key_valid_until=datetime.datetime.today()
    )
    new_record.save()


def get_all_vpn_keys_of_user(user_id: int) -> list:
    """
    Функция получения всех VPN ключей конкретного пользователя
    Params:
        userid: int
    Returns: list
    Exceptions: None
    """
    vpn_keys = \
        OutlineVPNKeys.objects.select_related('telegram_user_record').filter(telegram_user_record__telegram_id=user_id)
    if vpn_keys:
        to_return = []
        for vpn_key in vpn_keys:
            vpn_key_date = vpn_key.outline_key_valid_until
            if vpn_key_date:
                vpn_key_date = f'до: {vpn_key_date.strftime("%d-%m-%Y")!r}'
            else:
                vpn_key_date = 'без ограничений'

            to_return.append(f'ID: {vpn_key.outline_key_id!r} '
                             f'Ключ: {vpn_key.outline_key_value!r} '
                             f'Срок действия {vpn_key_date}')
        return to_return
    else:
        return []


def change_vpn_key_is_active(vpn_key: OutlineVPNKeys, test: bool = False) -> bool:
    """
    Функция изменения активности записи OutlineVPNKeys
    Params:
        vpn_key: OutlineVPNKeys
         test: bool = False - используется для Мока обращения к реальному outline серверу
    Returns: bool
    Exceptions: None
    """
    if vpn_key.outline_key_active:
        vpn_key.outline_key_active = False
        if not test:
            add_traffic_limit(vpn_key.outline_key_id)
    else:
        vpn_key.outline_key_active = True
        if not test:
            del_traffic_limit(vpn_key.outline_key_id)
    vpn_key.save()
    return vpn_key.outline_key_active


def change_vpn_key_valid_until(vpn_key: OutlineVPNKeys, days: int) -> datetime.datetime:
    """
    Функция изменения срока действия записи OutlineVPNKeys
    Params:
        vpn_key: OutlineVPNKeys
         days: int
    Returns:
        datetime.datetime
    Exceptions: None
    """
    if not days:
        vpn_key.outline_key_valid_until = None
    else:
        vpn_key.outline_key_valid_until = datetime.datetime.today() + datetime.timedelta(days=days)
    vpn_key.save()
    return vpn_key.outline_key_valid_until

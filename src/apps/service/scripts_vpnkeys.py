import datetime
import logging
from time import sleep

from django.db.models import QuerySet

from apps.service.bot.keyboards import main_keyboard
from apps.service.models import OutlineVPNKeys
from apps.service.bot.bot_main import bot


log = logging.getLogger(__name__)


def collect_expired_vpn_keys() -> QuerySet[OutlineVPNKeys]:
    """
    Функция получения всех просроченных VPN ключей
    Params: None
    Returns:
        QuerySet[OutlineVPNKeys]
    Exceptions: None
    """
    return OutlineVPNKeys.objects.select_related('telegram_user_record').filter(
        outline_key_active=True,
        outline_key_valid_until__lt=datetime.datetime.today(),
    )


def collect_expired_soon_vpn_keys(days_before_expire: int) -> QuerySet[OutlineVPNKeys]:
    """
    Функция получения всех VPN ключей, срок действия которых закончится через определенное количество дней
    Params:
        days_before_expire: int
    Returns:
        QuerySet[OutlineVPNKeys]
    Exceptions: None
    """
    target_date = datetime.datetime.today() + datetime.timedelta(days=days_before_expire)
    return OutlineVPNKeys.objects.select_related('telegram_user_record').filter(
        outline_key_active=True,
        outline_key_valid_until=target_date,
    )


def send_info_to_user(tg_user_id: int, msg: str) -> None:
    """
    Функция отправляет сообщение пользователю о блокировке ключа
    Params:
        tg_user_id: int,
        msg: str
    Returns: None
    Exceptions: None
    """
    bot.send_message(tg_user_id, msg, reply_markup=main_keyboard(tg_user_id))


def expire_vpn_key(test: bool = False) -> None:
    """
    Функция отключает все просроченные VPN ключи
    Params: test: bool = False - используется для мока доступа к серверу outline при тестировании
    Returns: None
    Exceptions: None
    """
    vpn_keys = collect_expired_vpn_keys()
    log.info(f'Ключей к деактивации - {len(vpn_keys)}')
    if vpn_keys:
        deactivated = 0
        for vpn_key in vpn_keys:
            vpn_key.outline_key_active = False
            vpn_key.add_traffic_limit(test=test)
            deactivated += 1
            if not test:
                send_info_to_user(
                    vpn_key.telegram_user_record.telegram_id,
                    f'Срок действия вашей подписки с VPN ключом {vpn_key.outline_key_id!r} истек.\n'
                    f'Для возобновления подписки свяжитесь с администратором.'
                )
            sleep(5)
        log.info(f'Ключей деактивировано - {deactivated}')


def expired_soon_vpn_keys() -> None:
    """
    Функция уведомляет пользователя о скором окончании действия  VPN ключа
    Params: None
    Returns: None
    Exceptions: None
    """
    days_before_expire = 7
    vpn_keys = collect_expired_soon_vpn_keys(days_before_expire)
    log.info(f'Пользователей к информированию - {len(vpn_keys)}')
    if vpn_keys:
        for vpn_key in vpn_keys:
            send_info_to_user(
                vpn_key.telegram_user_record.telegram_id,
                f'Срок действия вашей подписки с VPN ключом {vpn_key.outline_key_id!r}'
                f' истекает через {days_before_expire} дней.\n'
            )
        log.info(f'Пользователей проинформировано - {len(vpn_keys)}')

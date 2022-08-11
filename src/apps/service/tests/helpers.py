import datetime

from apps.service.models import TelegramUsers, OutlineVPNKeys


def create_telegram_users(cnt: int = 1) -> list[TelegramUsers]:
    """
    Функция для создания заданного количества пользователей в таблице TelegramUsers
    Params: None
    Returns: list[TelegramUsers]
    Exceptions: None
    """
    users = []
    for user_cnt in range(cnt):
        to_create = TelegramUsers(
            telegram_id=user_cnt,
            telegram_login=f'tg login test_{user_cnt}',
            telegram_first_name=f'tg first_name test_{user_cnt}',
            telegram_last_name=f'tg last_name test_{user_cnt}',
        )
        to_create.save()
        users.append(to_create)
    return users


def create_vpn_keys(cnt: int = 1) -> list[OutlineVPNKeys]:
    """
    Функция для создания заданного количества пользователей в таблице OutlineVPNKeys
    Params: None
    Returns: list[OutlineVPNKeys]
    Exceptions: None
    """
    users = create_telegram_users(cnt)
    vpns = []
    for vpn_cnt in range(cnt):
        to_create = OutlineVPNKeys(
            telegram_user_record=users[cnt - 1],
            outline_key_id=vpn_cnt,
            outline_key_name=f'test_{vpn_cnt}',
            outline_key_valid_until=datetime.datetime.now() + datetime.timedelta(days=vpn_cnt),
        )
        to_create.save()
        vpns.append(to_create)
    return vpns

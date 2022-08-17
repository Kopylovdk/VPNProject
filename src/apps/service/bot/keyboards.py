from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from apps.service.processes import get_all_admins


def main_keyboard(tg_user_id: int) -> ReplyKeyboardMarkup:
    """
    Основная клавиатура
    Params:
        admin_ids: list,
        tg_user_id: int
    Returns:
        ReplyKeyboardMarkup
    Exceptions: None
    """
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row_width = 3
    to_add_btn = [
        KeyboardButton(text='Оформить подписку'),
        KeyboardButton(text='Инструкция'),
        KeyboardButton(text='Поддержка'),
        KeyboardButton(text='Мои VPN ключи'),
    ]
    if tg_user_id in get_all_admins():
        to_add_btn.append(KeyboardButton(text='Режим администратора'))

    kb.add(*to_add_btn)
    return kb


def main_admin_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.row_width = 3
    kb.add(
        KeyboardButton(text='Список ключей пользователя'),
        KeyboardButton(text='Новый ключ'),
        KeyboardButton(text='Привязать ключ к пользователю'),
        KeyboardButton(text='Активация/продление ключа'),
        KeyboardButton(text='Удалить ключ'),
        KeyboardButton(text='Отправка сообщений'),
        KeyboardButton(text='Режим пользователя'),
    )
    return kb


def subscribe_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура вариантов подписки
    Params:
        subscribes: list
    Returns:
        ReplyKeyboardMarkup
    Exceptions: None
    """
    subscribes = ['Демо', '3 месяца', '6 месяцев']
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    subscribes_buttons = []
    for subscribe in subscribes:
        subscribes_buttons.append(KeyboardButton(text=subscribe))
    kb.add(*subscribes_buttons, KeyboardButton(text='В основное меню'))
    return kb


def bot_message_keyboard() -> ReplyKeyboardMarkup:
    """
    Клавиатура вариантов подписки
    Params: None
    Returns:
        ReplyKeyboardMarkup
    Exceptions: None
    """
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(
        KeyboardButton(text='Лично'),
        KeyboardButton(text='Всем'),
        KeyboardButton(text='В основное меню'),
    )
    return kb


def one_time_keyboard_cancel() -> ReplyKeyboardMarkup:
    """
    Вспомогательная клавиатура (клавиатура Отмена)
    Params: None
    Returns:
        ReplyKeyboardMarkup
    Exceptions: None
    """
    kb = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    kb.add(KeyboardButton(text='В основное меню'))
    return kb


def one_time_keyboard_send_edit() -> ReplyKeyboardMarkup:
    """
    Вспомогательная клавиатура (клавиатура Отмена)
    Params: None
    Returns:
        ReplyKeyboardMarkup
    Exceptions: None
    """
    kb = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
    kb.add(
        KeyboardButton(text='Отправить'),
        KeyboardButton(text='Редактировать'),
        KeyboardButton(text='В основное меню')
    )
    return kb


# def one_time_keyboard_yes_no() -> ReplyKeyboardMarkup:
#     """
#     Вспомогательная клавиатура (клавиатура Отмена)
#     Params: None
#     Returns:
#         ReplyKeyboardMarkup
#     Exceptions: None
#     """
#     kb = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
#     kb.add(
#         KeyboardButton(text='Да'),
#         KeyboardButton(text='Нет'),
#         KeyboardButton(text='В основное меню')
#     )
#     return kb


def one_time_keyboard_valid_active(is_active: bool, traffic_limit: int) -> ReplyKeyboardMarkup:
    """
    Вспомогательная клавиатура (клавиатура Отмена)
    Params: None
    Returns:
        ReplyKeyboardMarkup
    Exceptions: None
    """
    kb = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True, resize_keyboard=True)
    kb.add(
        KeyboardButton(text='Изменить срок действия'),
        KeyboardButton(text='Активировать' if not is_active else 'Деактивировать'),
        KeyboardButton(text='Установить лимит трафика' if not traffic_limit else 'Снять лимит трафика'),
        KeyboardButton(text='В основное меню')
    )
    return kb

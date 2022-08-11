from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from apps.service.processes import get_all_admins
from apps.service.models import TelegramUsers


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
        to_add_btn += [
            KeyboardButton(text='Новый ключ'),
            KeyboardButton(text='Привязать ключ к пользователю'),
            KeyboardButton(text='Удалить ключ'),
            KeyboardButton(text='Добавить срок действия'),
        ]

    kb.add(*to_add_btn)
    return kb


def subscribe_keyboard(subscribes: list) -> ReplyKeyboardMarkup:
    """
    Клавиатура вариантов подписки
    Params: None
    Returns: ReplyKeyboardMarkup
    Exceptions: None
    """
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    subscribes_buttons = []
    for subscribe in subscribes:
        subscribes_buttons.append(KeyboardButton(text=subscribe))
    kb.add(*subscribes_buttons, KeyboardButton(text='В основное меню'))
    return kb


def one_time_keyboard_yes_no() -> ReplyKeyboardMarkup:
    """
    Вспомогательная клавиатура (клавиатура да/нет)
    Params: None
    Returns: ReplyKeyboardMarkup
    Exceptions: None
    """
    kb = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    kb.add(KeyboardButton(text='да'), KeyboardButton(text='нет'))
    return kb


def one_time_keyboard_cancel() -> ReplyKeyboardMarkup:
    """
    Вспомогательная клавиатура (клавиатура Отмена)
    Params: None
    Returns: ReplyKeyboardMarkup
    Exceptions: None
    """
    kb = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    kb.add(KeyboardButton(text='В основное меню'))
    return kb

#
# def register_keyboard() -> ReplyKeyboardMarkup:
#     """
#     Вспомогательная клавиатура (клавиатура Зарегистрироваться)
#     Params: None
#     Returns: ReplyKeyboardMarkup
#     Exceptions: None
#     """
#     kb = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
#     kb.add(KeyboardButton(text='Зарегистрироваться'))
#     return kb

from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    to_add_btn = [
        KeyboardButton(text='Новый ключ'),
            # KeyboardButton(text='Доступные тарифы'),
            # KeyboardButton(text='Доступные сервера'),
        KeyboardButton(text='Действия с пользователем'),
        KeyboardButton(text='Действия с VPN ключом'),
        KeyboardButton(text='Отправка сообщений'),
            # KeyboardButton(text='Доступные боты'),
        KeyboardButton(text='Инструкция'),
    ]

    kb.add(*to_add_btn)
    return kb


def client_actions_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    to_add_btn = [
        KeyboardButton(text='Выбранный пользователь'),
        KeyboardButton(text='Список ВСЕХ ключей пользователя'),
        KeyboardButton(text='Сменить пользователя и/или бота'),
        KeyboardButton(text='В основное меню'),
    ]
    kb.add(*to_add_btn)
    return kb


def token_actions_keyboard(token_dict: dict) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    to_add_btn = [
        KeyboardButton(text='Информация о ключе'),
        KeyboardButton(text='Перевыпустить VPN ключ'),
        KeyboardButton(text='Изменить срок действия'),
        KeyboardButton(text='Установить лимит трафика' if not token_dict['traffic_limit'] else 'Снять лимит трафика'),
        KeyboardButton(text='Удалить ключ'),
        KeyboardButton(text='Выбрать другой VPN ключ'),
        KeyboardButton(text='В основное меню'),
    ]
    kb.add(*to_add_btn)
    return kb


def generate_action_keyboard(data: list) -> ReplyKeyboardMarkup:
    """Клавиатура с генерируемыми кнопками по полученному списку"""
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    buttons = []
    for text in data:
        buttons.append(KeyboardButton(text=text))
    kb.add(*buttons)
    kb.add(KeyboardButton(text='В основное меню'))
    return kb


def back_to_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура возврата в основное меню"""
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    kb.add(KeyboardButton(text='В основное меню'))
    return kb


def register_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(one_time_keyboard=True)
    kb.add(KeyboardButton(text="Регистрация", request_contact=True))
    return kb


def yes_no_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(
        KeyboardButton(text='Да'),
        KeyboardButton(text='Нет'),
    )
    return kb


def back_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    kb.add(
        KeyboardButton(text='Назад'),
    )
    return kb


def message_keyboard() -> ReplyKeyboardMarkup:
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
#

#
#
# def one_time_keyboard_send_edit() -> ReplyKeyboardMarkup:
#     """
#     Вспомогательная клавиатура (клавиатура отправки сообщений)
#     Params: None
#     Returns:
#         ReplyKeyboardMarkup
#     Exceptions: None
#     """
#     kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     kb.add(
#         KeyboardButton(text='Отправить'),
#         KeyboardButton(text='Редактировать'),
#         KeyboardButton(text='Назад'),
#     )
#     return kb


from telebot.types import ReplyKeyboardMarkup, KeyboardButton
# from apps.outline_vpn_admin.processes import get_all_admins


def main_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    to_add_btn = [
        # KeyboardButton(text='Регистрация', request_contact=True),
        KeyboardButton(text='Доступные тарифы'),
        KeyboardButton(text='Доступные боты'),
        KeyboardButton(text='Инструкция'),

        KeyboardButton(text='Отправка сообщений'),

        KeyboardButton(text='Получить информацию о пользователе'),

        KeyboardButton(text='Список ключей пользователя'),
        KeyboardButton(text='Информация о ключе'),
        KeyboardButton(text='Перевыпустить VPN ключ'),

        KeyboardButton(text='Новый ключ'),
        KeyboardButton(text='Действия с API ключом'),


        # KeyboardButton(text='Привязать ключ к пользователю'),
        # KeyboardButton(text='Изменить срок действия'),
        # KeyboardButton(text='Активировать' if not is_active else 'Деактивировать'),
        # KeyboardButton(text='Установить лимит трафика' if not traffic_limit else 'Снять лимит трафика'),
        # KeyboardButton(text='Изменить имя'),
        # KeyboardButton(text='Удалить ключ'),
        # KeyboardButton(text='В основное меню'),
    ]
    kb.add(*to_add_btn)
    return kb


def generate_action_keyboard(data: list = None) -> ReplyKeyboardMarkup:
    """Клавиатура с генерируемыми кнопками по полученному списку"""
    if not data:
        data = ['No_data_1', 'No_data_2', 'No_data_3']

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

#
# def bot_message_keyboard() -> ReplyKeyboardMarkup:
#     """
#     Клавиатура вариантов подписки
#     Params: None
#     Returns:
#         ReplyKeyboardMarkup
#     Exceptions: None
#     """
#     kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     kb.add(
#         KeyboardButton(text='Лично'),
#         KeyboardButton(text='Всем'),
#         KeyboardButton(text='В основное меню'),
#     )
#     return kb
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


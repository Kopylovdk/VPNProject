from telebot.types import ReplyKeyboardMarkup, KeyboardButton
# from apps.outline_vpn_admin.processes import get_all_admins


def main_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    to_add_btn = [
        KeyboardButton(text='Регистрация', request_contact=True),
        KeyboardButton(text='Доступные тарифы'),
        KeyboardButton(text='Оформить подписку'),

        KeyboardButton(text='Мои VPN ключи'),
        KeyboardButton(text='Перевыпустить VPN ключ'),
        KeyboardButton(text='Инструкция'),

        KeyboardButton(text='Поддержка'),
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


# def main_keyboard(tg_user_id: int) -> ReplyKeyboardMarkup:
#     """
#     Основная клавиатура
#     Params:
#         admin_ids: list,
#         tg_user_id: int
#     Returns:
#         ReplyKeyboardMarkup
#     Exceptions: None
#     """
#     kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
#     to_add_btn = [
#         KeyboardButton(text='Оформить подписку'),
#         KeyboardButton(text='Инструкция'),
#         KeyboardButton(text='Поддержка'),
#         KeyboardButton(text='Мои VPN ключи'),
#     ]
#     if tg_user_id in get_all_admins():
#         to_add_btn.append(KeyboardButton(text='Режим администратора'))
#
#     kb.add(*to_add_btn)
#     return kb
#
#
# def main_admin_keyboard() -> ReplyKeyboardMarkup:
#     kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
#     kb.add(
#         KeyboardButton(text='Список ключей пользователя'),
#         KeyboardButton(text='Новый ключ'),
#         KeyboardButton(text='Редактирование VPN ключа'),
#         KeyboardButton(text='Отправка сообщений'),
#         KeyboardButton(text='Памятка администратора'),
#         KeyboardButton(text='Режим пользователя'),
#     )
#     return kb
#
# #
# def subscribe_keyboard() -> ReplyKeyboardMarkup:
#     """
#     Клавиатура вариантов подписки
#     Params:
#         subscribes: list
#     Returns:
#         ReplyKeyboardMarkup
#     Exceptions: None
#     """
#     subscribes = ['Демо', '3 месяца', '6 месяцев']
#     kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
#     subscribes_buttons = []
#     for subscribe in subscribes:
#         subscribes_buttons.append(KeyboardButton(text=subscribe))
#     kb.add(*subscribes_buttons, KeyboardButton(text='В основное меню'))
#     return kb

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
# def one_time_keyboard_back_to_main() -> ReplyKeyboardMarkup:
#     """
#     Вспомогательная клавиатура (клавиатура Отмена)
#     Params: None
#     Returns:
#         ReplyKeyboardMarkup
#     Exceptions: None
#     """
#     kb = ReplyKeyboardMarkup(resize_keyboard=True)
#     kb.add(KeyboardButton(text='В основное меню'))
#     return kb
#
#
# def one_time_keyboard_back() -> ReplyKeyboardMarkup:
#     """
#     Вспомогательная клавиатура (клавиатура Отмена)
#     Params: None
#     Returns:
#         ReplyKeyboardMarkup
#     Exceptions: None
#     """
#     kb = ReplyKeyboardMarkup(resize_keyboard=True)
#     kb.add(KeyboardButton(text='Назад'))
#     return kb
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
#
#
# def vpn_key_edit_actions_keyboard(is_active: bool, traffic_limit: int) -> ReplyKeyboardMarkup:
#     """
#     Вспомогательная клавиатура (клавиатура Отмена)
#     Params: None
#     Returns:
#         ReplyKeyboardMarkup
#     Exceptions: None
#     """
#     kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     kb.add(
#         KeyboardButton(text='Привязать ключ к пользователю'),
#         KeyboardButton(text='Изменить срок действия'),
#         KeyboardButton(text='Активировать' if not is_active else 'Деактивировать'),
#         KeyboardButton(text='Установить лимит трафика' if not traffic_limit else 'Снять лимит трафика'),
#         KeyboardButton(text='Изменить имя'),
#         KeyboardButton(text='Удалить ключ'),
#         KeyboardButton(text='В основное меню'),
#     )
#     return kb
#
#
# def delete_keyboard() -> ReplyKeyboardMarkup:
#     """
#     Вспомогательная клавиатура (клавиатура удаления)
#     Params: None
#     Returns:
#         ReplyKeyboardMarkup
#     Exceptions: None
#     """
#     kb = ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
#     kb.add(
#         KeyboardButton(text='Удалить'),
#         KeyboardButton(text='Назад'),
#     )
#     return kb

from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard(admin_ids: list, tg_user_id: int) -> ReplyKeyboardMarkup:
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
    if tg_user_id in admin_ids:
        kb.row_width = 3
        to_add_btn = [
            KeyboardButton(text='Получить TG id пользователя'),
            KeyboardButton(text='Новый ключ'),
            KeyboardButton(text='Удалить ключ'),
            KeyboardButton(text='Список ключей'),
            KeyboardButton(text='Добавить имя'),
            KeyboardButton(text='Добавить срок действия'),
        ]
    else:
        kb.row_width = 2
        to_add_btn = [
            KeyboardButton(text='Оформить подписку'),
            KeyboardButton(text='Инструкция'),
            KeyboardButton(text='Поддержка'),
        ]
    kb.add(*to_add_btn)
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
    kb.add(KeyboardButton(text='отмена'))
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

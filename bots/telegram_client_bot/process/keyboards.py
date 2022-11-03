from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def main_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура"""
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    to_add_btn = [
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
    kb.add(*buttons, KeyboardButton(text='В основное меню'))
    return kb


def back_to_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура возврата в основное меню"""
    kb = ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    kb.add(KeyboardButton(text='В основное меню'))
    return kb

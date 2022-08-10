from telebot import TeleBot
from telebot.types import Message
from apps.service.bot.processes import add_new_tg_user
from apps.service.bot.keyboards import main_keyboard
from vpnservice.settings import EXTERNAL_CFG


tg_bot_conf = EXTERNAL_CFG['tg_bot']
bot = TeleBot(tg_bot_conf['token'])


@bot.message_handler(commands=['start'])
def start(message: Message):
    """Хендлер команды Start"""
    tg_user = message.from_user
    bot.send_message(
        message.chat.id,
        text='Добро пожаловать в VPN Project!',
        reply_markup=main_keyboard(tg_bot_conf['admin_ids'], tg_user.id)
    )
    add_new_tg_user(tg_user)


@bot.message_handler(content_types=["text"])
def handle_text(message: Message):
    """Хендлер обработки текстовых команд клавиатуры от пользователя"""
    tg_user = message.from_user
    if 'Оформить подписку' in message.text:
        bot.send_message(tg_user.id, text='в разработке')

    elif 'Инструкция' in message.text:
        bot.send_message(tg_user.id, text='в разработке')

    elif 'Поддержка' in message.text:
        bot.send_message(tg_user.id, text='в разработке')

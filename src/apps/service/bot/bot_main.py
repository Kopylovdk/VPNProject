from telebot import TeleBot
import threading
from outline_vpn.outline_vpn import OutlineVPN
from telebot.types import Message
import yaml
import os


with open(f'{os.getcwd()}/config.yaml', 'r', encoding='utf8') as f:
    config = yaml.safe_load(f)
    outline_conf = config['outline_vpn']
    tg_bot_conf = config['tg_bot']


outline_client = OutlineVPN("https://{}:{}/{}".format(**outline_conf))

bot = TeleBot(tg_bot_conf['token'])


@bot.message_handler(commands=['start'])
def start(message: Message):
    """Хендлер команды Start"""
    bot.send_message(message.chat.id, 'Добро пожаловать в VPN Project!')
    # TODO: регистрация пользователя ТГ в постгрес, Вернуть клавиатуру управления по ТГ ID


@bot.message_handler(content_types=["text"])
def handle_text(message: Message):
    """Хендлер обработки текстовых сообщений от пользователя"""


threading.Thread(bot.polling(none_stop=True, interval=0), name='telegram_thread_v1')

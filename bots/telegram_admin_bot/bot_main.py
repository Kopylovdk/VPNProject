import logging
import os
import sys
from telebot import TeleBot
from telebot.types import Message
from process.bot_processes import (
    health_check,
    get_auth_api_headers,
    get_tariffs,
    get_vpn_servers,
    get_transports,
    send_alert_to_admins,
    add_or_update_user,
    select_action_with_token_step_1,
    select_action_with_user_step_1,
    new_token_step_1,
    select_message_send_type_step_1,
    ADMIN_ACCESS
)
from process.keyboards import main_keyboard, register_keyboard


log = logging.getLogger(__name__)
bot = TeleBot(os.environ.get("TELEGRAM_TOKEN"))


@bot.message_handler(commands=['start'])
def start(message: Message):
    """Обработчик команды Start"""
    if message.from_user.id in ADMIN_ACCESS:
        bot.send_message(
            message.chat.id,
            text='Добро пожаловать в VPN Project!',
            reply_markup=register_keyboard(),
        )
    else:
        bot.send_message(message.chat.id, text='Доступ запрещен')


@bot.message_handler(content_types=["contact"])
def contact_handler(message: Message):
    add_or_update_user(bot=bot, message=message)


@bot.message_handler(content_types=["text"])
def handle_text(message: Message):
    """Обработчик текстовых команд клавиатуры от пользователя"""
    tg_user = message.from_user
    if tg_user.id not in ADMIN_ACCESS:
        bot.send_message(message.chat.id, text='Доступ запрещен')
    else:
        user_answer = message.text
        if 'Новый ключ' in user_answer:
            new_token_step_1(bot=bot, message=message)
        elif 'Действия с пользователем' in user_answer:
            select_action_with_user_step_1(bot=bot, message=message)
        elif 'Действия с VPN ключом' in user_answer:
            select_action_with_token_step_1(bot=bot, message=message)
        elif 'Отправка сообщений' in user_answer:
            select_message_send_type_step_1(bot=bot, message=message)

        elif 'Инструкция' in user_answer:
            with open('instruction/instructions.txt', 'r') as f:
                instruction = f.read()
            bot.send_message(
                tg_user.id,
                text=instruction,
                reply_markup=main_keyboard(),
            )
        else:
            bot.send_message(
                tg_user.id,
                text=f'Такой команды не существует. Выберите действие на клавиатуре.\n',
                reply_markup=main_keyboard(),
            )


if __name__ == '__main__':
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)-8s [%(name)s] [line=%(lineno)s] [msg=%(message)s]',
    )

    # TODO: таймер проверки
    response = health_check()
    if response.status_code != 200:
        send_alert_to_admins(bot=bot, response=response)
    else:
        # add to cache
        get_auth_api_headers(bot=bot)
        get_tariffs(bot=bot)
        get_vpn_servers(bot=bot)
        get_transports(bot=bot)

    bot.infinity_polling(non_stop=True, interval=0)

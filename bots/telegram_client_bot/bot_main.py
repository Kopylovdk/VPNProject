import logging
import os
import sys
from telebot import TeleBot
from telebot.types import Message
from process.bot_processes import (
    send_msg_to_managers,
    add_or_update_user,
    get_vpn_keys,
    send_alert_to_admins,
    health_check,
    get_auth_api_headers,
    get_tariffs,
    get_vpn_servers,
    renew_token_step_1,
    subscribes_step_1,
    tariffs_step_1,
    check_cache_date,
)
from process.keyboards import main_keyboard, register_keyboard


log = logging.getLogger(__name__)
bot = TeleBot(os.environ.get("TELEGRAM_TOKEN"))


@bot.message_handler(commands=['start'])
def start(message: Message):
    """Обработчик команды Start"""
    bot.send_message(
        message.chat.id,
        text='Добро пожаловать в VPN Project!',
        reply_markup=register_keyboard(),
    )


@bot.message_handler(content_types=["contact"])
def contact_handler(message: Message):
    add_or_update_user(bot=bot, message=message)


@bot.message_handler(content_types=["text"])
def handle_text(message: Message):
    """Обработчик текстовых команд клавиатуры от пользователя"""
    tg_user = message.from_user
    user_answer = message.text
    if 'Оформить подписку' in user_answer:
        subscribes_step_1(
            bot=bot,
            message=message,
        )

    elif 'Перевыпустить VPN ключ' in user_answer:
        renew_token_step_1(
            bot=bot,
            message=message,
        )

    elif 'Мои VPN ключи' in user_answer:
        get_vpn_keys(
            bot=bot,
            user=tg_user,
        )

    elif 'Доступные тарифы' in user_answer:
        tariffs_step_1(
            bot=bot,
            message=message
        )

    elif 'Инструкция' in user_answer:
        with open('instruction/instructions.txt', 'r') as f:
            instruction = f.read()
        bot.send_message(
            tg_user.id,
            text=instruction,
            reply_markup=main_keyboard(),
        )
    elif 'Поддержка' in message.text:
        send_msg_to_managers(bot=bot, text='Требуется помощь администратора.', message=message)
        bot.send_message(
            tg_user.id,
            text='Администратор свяжется с Вами в ближайшее время.',
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
        check_cache_date(bot=bot)
        get_tariffs(bot=bot)
        get_vpn_servers(bot=bot)

    bot.infinity_polling(interval=1)

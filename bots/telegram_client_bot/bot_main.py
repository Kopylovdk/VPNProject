import logging
import sys

from config_loader import CONFIG
from telebot import TeleBot
from telebot.types import Message, User
from bot_processes import (
    send_msg_to_admins, add_or_update_user, get_vpn_keys, send_alert_to_admins, health_check,
    # user_vpn_keys_list_step_1,
    # messages_send_choice_step_1,
    # bot_create_key,
)

from keyboards import (
    main_keyboard,
    generate_action_keyboard,
)

bot = TeleBot(CONFIG['bot']['telegram_token'])


@bot.message_handler(commands=['start'])
def start(message: Message):
    """Обработчик команды Start"""
    bot.send_message(
        message.chat.id,
        text='Добро пожаловать в VPN Project!',
        reply_markup=main_keyboard(),
    )
    add_or_update_user(message.from_user)


@bot.message_handler(content_types=["text"])
def handle_text(message: Message):
    """Обработчик текстовых команд клавиатуры от пользователя"""
    tg_user = message.from_user
    add_or_update_user(tg_user)
    if 'Оформить подписку' in message.text:
        pass
    elif 'Перевыпустить VPN ключ' in message.text:
        pass
    elif 'Мои VPN ключи' in message.text:
        data, msg = get_vpn_keys(tg_user)
        if isinstance(data, list):
            bot.send_message(tg_user.id, '\n'.join(data) if data else 'Ключи отсутствуют', reply_markup=main_keyboard())
        else:
            bot.send_message(tg_user.id, data, reply_markup=main_keyboard())
            send_alert_to_admins(bot=bot, user=tg_user, text=msg)
    elif 'Инструкция' in message.text:
        with open('instruction/instructions.txt', 'r') as f:
            instruction = f.read()
        bot.send_message(
            tg_user.id,
            text=instruction,
            reply_markup=main_keyboard(),
        )
    elif 'Поддержка' in message.text:
        send_msg_to_admins(bot=bot, user=tg_user, text='Требуется помощь администратора.', message=message)
        bot.send_message(
            tg_user.id,
            text='Администратор свяжется с Вами в ближайшее время.',
            reply_markup=main_keyboard(),
        )
    else:
        bot.send_message(
            tg_user.id,
            text=f'Такой команды не существует. Выберите действие на клавиатуре.\n{health_check()=}\n',
            reply_markup=main_keyboard(),
        )


if __name__ == '__main__':
    logging.basicConfig(
        stream=sys.stderr,
        level=logging.DEBUG,
        format='[%(asctime)s] %(levelname)-8s [%(name)s] [line=%(lineno)s] [msg=%(message)s]',
    )
    bot.polling(none_stop=True, interval=0)

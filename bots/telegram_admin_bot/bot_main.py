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
        get_tariffs(bot=bot)
        get_vpn_servers(bot=bot)

    bot.polling(none_stop=True, interval=0)


# from process.config_loader import CONFIG
# from telebot import TeleBot
# from telebot.types import Message
#
# # from telegram_client_bot.bot_processes import (
# #     api_key_edit_step_1,
# #     user_vpn_keys_list_step_1,
# #     messages_send_choice_step_1,
# #     bot_create_key,
# # )
# # from apps.outline_vpn_admin.processes import (
# #     get_all_admins,
# #     add_new_tg_user,
# #     get_all_vpn_keys_of_user,
# # )
# # from telegram_client_bot.keyboards import (
# #     main_keyboard,
# #     subscribe_keyboard,
# #     main_admin_keyboard,
# # )
#
#
#
# # tg_bot_conf = EXTERNAL_CFG['tg_bot']
# bot = TeleBot(CONFIG['bot']['telegram_token'])
#
#
# # def send_msg_to_admins(user: User, text: str) -> None:
# #     """
# #     Функция отправки сообщений всем администратора
# #     Params:
# #         user: User
# #     Returns: None
# #     Exceptions: None
# #     """
# #     admin_ids = get_all_admins()
# #     for admin_id in admin_ids:
# #         bot.send_message(
# #             admin_id,
# #             text=f'Пользователь:\n'
# #                  f'ID - {user.id!r}\n'
# #                  f'Логин - {user.username!r}\n'
# #                  f'ФИО - {user.full_name!r}\n'
# #                  f'{text}',
# #         )
# #
# #
# @bot.message_handler(commands=['start'])
# def start(message: Message):
#     """Обработчик команды Start"""
#     tg_user = message.from_user
#     bot.send_message(
#         message.chat.id,
#         text='Добро пожаловать в VPN Project!',
#         reply_markup=main_keyboard(tg_user.id),
#     )
#     add_new_tg_user(tg_user.to_dict())
#
# #
# # @bot.message_handler(content_types=["text"])
# # def handle_text(message: Message):
# #     """Обработчик обработки текстовых команд клавиатуры от пользователя"""
# #     tg_user = message.from_user
# #     add_new_tg_user(tg_user.to_dict())
# #     if 'Оформить подписку' in message.text:
# #         bot.send_message(
# #             tg_user.id,
# #             text='Выберите вариант подписки',
# #             reply_markup=subscribe_keyboard(),
# #         )
# #
# #     elif 'Демо' in message.text:
# #         vpn_key = bot_create_key(VPN_SERVER_NAME, tg_user.id)
# #         bot.send_message(
# #             message.chat.id,
# #             f'Ваш демо ключ: {vpn_key.outline_key_value!r}\n'
# #             f'Воспользуйтесь Инструкцией для дальнейшей работы с сервисом',
# #             reply_markup=main_keyboard(tg_user.id),
# #         )
# #         send_msg_to_admins(tg_user, f'получил демо ключ. ID ключа - {vpn_key.outline_key_id!r}')
# #
# #     elif message.text in ['3 месяца', '6 месяцев']:
# #         bot.send_message(
# #             tg_user.id,
# #             text='Для оплаты подписки с Вами свяжется Администратор.',
# #             reply_markup=main_keyboard(tg_user.id),
# #         )
# #         send_msg_to_admins(user=tg_user, text=f'Хочет оплатить подписку на {message.text!r}')
# #
# #     elif 'Мои VPN ключи' in message.text:
# #         vpn_keys = get_all_vpn_keys_of_user(tg_user.id)
# #         bot.send_message(
# #             tg_user.id,
# #             '\n'.join(vpn_keys) if vpn_keys else 'Ключи отсутствуют, если это не так - обратитесь к администратору.',
# #             reply_markup=main_keyboard(tg_user.id),
# #         )
# #
# #     elif 'Инструкция' in message.text:
# #         with open('telegram_client_bot/instructions.txt', 'r') as f:
# #             instruction = f.read()
# #         bot.send_message(
# #             tg_user.id,
# #             text=instruction,
# #             reply_markup=main_keyboard(tg_user.id),
# #         )
# #
# #     elif 'Памятка администратора' in message.text:
# #         with open('telegram_client_bot/instructions_admin.txt', 'r') as fa:
# #             instruction = fa.read()
# #         bot.send_message(
# #             tg_user.id,
# #             text=instruction,
# #             reply_markup=main_admin_keyboard(),
# #         )
# #
# #     elif 'Поддержка' in message.text:
# #         send_msg_to_admins(user=tg_user, text='Требуется помощь администратора')
# #         bot.send_message(
# #             tg_user.id,
# #             text='Администратор свяжется с Вами в ближайшее время.',
# #             reply_markup=main_keyboard(tg_user.id),
# #         )
# #
# #     elif 'Режим администратора' in message.text:
# #         bot.send_message(
# #             tg_user.id,
# #             text='Режим Администратора включен',
# #             reply_markup=main_admin_keyboard(),
# #         )
# #     elif 'Режим пользователя' in message.text:
# #         bot.send_message(
# #             tg_user.id,
# #             text='Режим Администратора выключен',
# #             reply_markup=main_keyboard(tg_user.id),
# #         )
# #     elif 'Список ключей пользователя' in message.text:
# #         user_vpn_keys_list_step_1(message, bot)
# #
# #     elif 'Новый ключ' in message.text:
# #         vpn_key = bot_create_key(VPN_SERVER_NAME)
# #         bot.send_message(tg_user.id, f'Ключ создан.\nvpn_key_id={vpn_key.outline_key_id!r}\nлимит трафика 1 кб.')
# #
# #     elif 'Редактирование VPN ключа' in message.text:
# #         api_key_edit_step_1(message, bot, VPN_SERVER_NAME)
# #
# #     elif 'Отправка сообщений' in message.text:
# #         messages_send_choice_step_1(message, bot)
# #
# #     elif 'В основное меню' in message.text:
# #         bot.send_message(tg_user.id, 'Возврат в основное меню', reply_markup=main_keyboard(tg_user.id))
# #     else:
# #         bot.send_message(
# #             tg_user.id,
# #             text='Такой команды не существует.',
# #             reply_markup=main_keyboard(tg_user.id),
# #         )
# #
# #
# # #  TODO: сделать бот отдельным, очередь, АПИ

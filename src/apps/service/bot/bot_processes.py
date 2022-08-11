from telebot import TeleBot
from telebot.types import Message
from apps.service.bot.keyboards import main_keyboard, one_time_keyboard_cancel
from apps.service.outline.outline_api import delete_key
from apps.service.processes import add_new_vpn_key_to_tg_user, get_tg_user_by_, get_outline_key_by_id


def validate_int(data: str) -> bool:
    try:
        int(data)
        return True
    except ValueError:
        return False


def add_new_vpn_key_to_tg_user_step_1(message: Message, bot: TeleBot):
    bot.send_message(
        message.chat.id,
        'Для привязки VPN к пользователю, введите через пробел:\n'
        '- id VPN ключа\n'
        '- логин пользователя TG или его ID\n'
        'Пример: 1 login или 1 123456',
        reply_markup=one_time_keyboard_cancel()
    )
    bot.register_next_step_handler(message, add_new_vpn_key_to_tg_user_step_2, bot)


def add_new_vpn_key_to_tg_user_step_2(message: Message, bot: TeleBot):
    if 'В основное меню' in message.text:
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_keyboard(message.from_user.id))
    else:
        data = message.text.split(' ')
        if len(data) == 2:
            if validate_int(data[0]):
                outline_vpn_record = get_outline_key_by_id(int(data[0]))
                if not outline_vpn_record:
                    if validate_int(data[1]):
                        tg_user = get_tg_user_by_(telegram_id=int(data[1]))
                    else:
                        tg_user = get_tg_user_by_(telegram_login=data[1])
                    if tg_user:
                        add_new_vpn_key_to_tg_user(int(data[0]), tg_user.id)
                        bot.send_message(
                            message.chat.id,
                            f'VPN ключ {data[0]} привязан к пользователю {tg_user.telegram_id}.',
                            reply_markup=main_keyboard(message.from_user.id))
                    else:
                        bot.send_message(message.chat.id, f'Пользователь {data[1]} не найден. Повторите ввод данных.')
                        bot.register_next_step_handler(message, add_new_vpn_key_to_tg_user_step_2, bot)
                else:
                    bot.send_message(
                        message.chat.id,
                        f'VPN ключ {data[0]} уже зарегистрирован за пользователем'
                        f' {outline_vpn_record.telegram_user_record.telegram_id}. Повторите ввод данных.'
                    )
                    bot.register_next_step_handler(message, add_new_vpn_key_to_tg_user_step_2, bot)
            else:
                bot.send_message(message.chat.id, f'VPN id не целое число: {data[0]}. Повторите ввод данных.')
                bot.register_next_step_handler(message, add_new_vpn_key_to_tg_user_step_2, bot)
        else:
            bot.send_message(message.chat.id, f'Некорректные параметры, значений должно быть 2. Повторите ввод данных.')
            bot.register_next_step_handler(message, add_new_vpn_key_to_tg_user_step_2, bot)


def delete_step_1(message: Message, bot: TeleBot):
    bot.send_message(
        message.chat.id,
        'Для удаления VPN ключа введите его ID:\n',
        reply_markup=one_time_keyboard_cancel()
    )
    bot.register_next_step_handler(message, delete_step_2, bot)


def delete_step_2(message: Message, bot: TeleBot):
    if 'В основное меню' in message.text:
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_keyboard(message.from_user.id))
    else:
        if validate_int(message.text):
            vpn_key_id = int(message.text)
            outline_vpn_record = get_outline_key_by_id(vpn_key_id)
            if outline_vpn_record:
                outline_vpn_record.delete()
            bot.send_message(
                message.chat.id,
                delete_key(vpn_key_id),
                reply_markup=main_keyboard(message.from_user.id)
            )
        else:
            bot.send_message(message.chat.id, f'VPN id не целое число: {message.text}. Повторите ввод данных.')
            bot.register_next_step_handler(message, delete_step_2, bot)


# def name_add_step_1(message: Message, bot: TeleBot, client: OutlineVPN):
#     message = bot.reply_to(
#         message,
#         "Вы хотите добавить имя ключу?\n"
#         "Если да, то на следующем шаге укажите ID ключа\n"
#         "Если Вы не знаете ID - то посмотреть его можно получив весь список ключей",
#         reply_markup=one_time_keyboard_yes_no()
#     )
#     bot.register_next_step_handler(message, name_add_step_2, bot, client)
#
#
# def name_add_step_2(message: Message, bot: TeleBot, client: OutlineVPN):
#     if message.text == 'да':
#         message = bot.send_message(
#             message.chat.id, f"Введите id ключа для добавления имени.",
#             reply_markup=one_time_keyboard_cancel()
#         )
#         bot.register_next_step_handler(message, name_add_step_3, bot, client)
#     elif message.text == 'нет':
#         bot.send_message(message.chat.id, 'Возврат в основное меню.', reply_markup=admin_keyboard())
#     else:
#         bot.send_message(
#             message.chat.id,
#             'Неизвестная команда. Возврат в основное меню',
#             reply_markup=admin_keyboard()
#         )
#
#
# def name_add_step_3(message: Message, bot: TeleBot, client: OutlineVPN):
#     if message.text == 'отмена':
#         bot.send_message(message.chat.id, 'Возврат в основное меню.', reply_markup=admin_keyboard())
#     else:
#         key_id = message.text
#         message = bot.send_message(
#             message.chat.id, f"Введите Имя ключа.",
#             reply_markup=one_time_keyboard_cancel()
#         )
#         bot.register_next_step_handler(message, name_add_step_4, bot, client, key_id)
#
#
# def name_add_step_4(message: Message, bot: TeleBot, client: OutlineVPN, key_id):
#     if message.text == 'отмена':
#         bot.send_message(message.chat.id, 'Возврат в основное меню.', reply_markup=admin_keyboard())
#     else:
#         bot.send_message(message.chat.id, name_add(client, key_id, message.text))
#         bot.send_message(message.chat.id, 'Возврат в основное меню.', reply_markup=admin_keyboard())
#

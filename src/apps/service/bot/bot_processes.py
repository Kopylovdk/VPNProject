from telebot import TeleBot
from telebot.types import Message
from apps.service.bot.keyboards import(
    main_keyboard,
    one_time_keyboard_cancel,
    one_time_keyboard_send_edit,
    one_time_keyboard_yes_no,
)
from apps.service.models import TelegramUsers, OutlineVPNKeys
from apps.service.outline.outline_api import delete_key
from apps.service.processes import (
    add_new_vpn_key_to_tg_user,
    get_tg_user_by_,
    get_outline_key_by_id,
    change_vpn_key_is_active,
    change_vpn_key_valid_until,
    get_all_no_admin_users,
)


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


def active_prolong_api_key_step_1(message: Message, bot: TeleBot):
    bot.send_message(
        message.chat.id,
        'Для активации/деактивации ключа, введите ID VPN ключа\n',
        reply_markup=one_time_keyboard_cancel()
    )
    bot.register_next_step_handler(message, active_prolong_api_key_step_2, bot)


def active_prolong_api_key_step_2(message: Message, bot: TeleBot):
    if 'В основное меню' in message.text:
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_keyboard(message.from_user.id))
    else:
        if validate_int(message.text):
            outline_vpn_record = get_outline_key_by_id(int(message.text))
            if outline_vpn_record:
                key_status = change_vpn_key_is_active(outline_vpn_record)
                bot.send_message(
                    message.chat.id,
                    f'VPN ключ {outline_vpn_record.outline_key_id!r}'
                    f' {"АКТИВИРОВАН" if key_status else "ДЕАКТИВИРОВАН"},\n'
                    f'Лимит трафика {"Снят" if key_status else "Установлен"}\n'
                )
                bot.send_message(
                    message.chat.id,
                    'Требуется изменения срока действия?',
                    reply_markup=one_time_keyboard_yes_no()
                )
                bot.register_next_step_handler(message, active_prolong_api_key_step_3, bot, outline_vpn_record)

            else:
                bot.send_message(
                    message.chat.id,
                    f'VPN ключ {message.text} не зарегистрирован ни за одним пользователем. Повторите ввод данных.'
                )
                bot.register_next_step_handler(message, active_prolong_api_key_step_2, bot)
        else:
            bot.send_message(message.chat.id, f'VPN id не целое число: {message.text}. Повторите ввод данных.')
            bot.register_next_step_handler(message, active_prolong_api_key_step_2, bot)


def active_prolong_api_key_step_3(message: Message, bot: TeleBot, outline_vpn_record: OutlineVPNKeys):
    if 'В основное меню' in message.text or 'Нет ' in message.text:
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_keyboard(message.from_user.id))
    elif 'Да' in message.text:
        bot.send_message(
            message.chat.id,
            'Ведите срок действия ключа в днях. Если указать 0 - ключ будет без ограничения по времени.',
            reply_markup=one_time_keyboard_cancel()
        )
        bot.register_next_step_handler(message, active_prolong_api_key_step_4, bot, outline_vpn_record)


def active_prolong_api_key_step_4(message: Message, bot: TeleBot, outline_vpn_record: OutlineVPNKeys):
    if 'В основное меню' in message.text:
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_keyboard(message.from_user.id))
    else:
        if validate_int(message.text):
            valid_until = change_vpn_key_valid_until(outline_vpn_record, int(message.text))
            outline_vpn_record.refresh_from_db()
            if not valid_until:
                msg = 'без ограничений'
            else:
                msg = f'до {valid_until!r}'
            bot.send_message(
                message.chat.id,
                f'На VPN ключ {outline_vpn_record.outline_key_id!r} установлен срок действия {msg}',
                reply_markup=main_keyboard(message.from_user.id)
            )
        else:
            bot.send_message(
                message.chat.id,
                f'Количество дней не целое число: {message.text}. Повторите ввод данных.'
            )
            bot.register_next_step_handler(message, active_prolong_api_key_step_4, bot, outline_vpn_record)


def personal_message_send_step_1(message: Message, bot: TeleBot):
    bot.send_message(
        message.chat.id,
        'Укажите TG id пользователя или его логин:\n',
        reply_markup=one_time_keyboard_cancel()
    )
    bot.register_next_step_handler(message, personal_message_send_step_2, bot)


def personal_message_send_step_2(message: Message, bot: TeleBot):
    if 'В основное меню' in message.text:
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_keyboard(message.from_user.id))
    else:
        if validate_int(message.text):
            tg_user = get_tg_user_by_(telegram_id=int(message.text))
        else:
            tg_user = get_tg_user_by_(telegram_login=message.text)
        if tg_user:
            bot.send_message(
                message.chat.id,
                f'Введите сообщение для пользователя:',
                reply_markup=one_time_keyboard_cancel()
            )
            bot.register_next_step_handler(message, personal_message_send_step_3, bot, tg_user)
        else:
            bot.send_message(message.chat.id, f'Пользователь {message.text} не найден. Повторите ввод данных.')
            bot.register_next_step_handler(message, add_new_vpn_key_to_tg_user_step_2, bot)


def personal_message_send_step_3(message: Message, bot: TeleBot, tg_user: TelegramUsers):
    if 'В основное меню' in message.text:
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_keyboard(message.from_user.id))
    else:
        bot.send_message(tg_user.telegram_id, f'Сообщение от администратора:\n{message.text}')
        bot.send_message(
            message.chat.id,
            f'Сообщение для пользователя {tg_user.telegram_login} - {tg_user.telegram_id} отправлено.\n'
            f'Копия сообщения:\n {message.text}',
            reply_markup=main_keyboard(message.from_user.id)
        )


def all_users_message_send_step_1(message: Message, bot: TeleBot):
    bot.send_message(
        message.chat.id,
        'Введите сообщение для всех пользователей\n',
        reply_markup=one_time_keyboard_cancel()
    )
    bot.register_next_step_handler(message, all_users_message_send_step_2, bot)


def all_users_message_send_step_2(message: Message, bot: TeleBot):
    if 'В основное меню' in message.text:
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_keyboard(message.from_user.id))
    else:
        bot.send_message(
            message.chat.id,
            f'Проверьте сообщение: {message.text}',
            reply_markup=one_time_keyboard_send_edit()
        )
        bot.register_next_step_handler(message, all_users_message_send_step_3, bot)


def all_users_message_send_step_3(message: Message, bot: TeleBot):
    if 'В основное меню' in message.text:
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_keyboard(message.from_user.id))
    elif 'Редактировать' in message.text:
        bot.register_next_step_handler(message, all_users_message_send_step_1, bot)
    elif 'Отправить' in message.text:
        tg_users_ids = get_all_no_admin_users()
        for user_id in tg_users_ids:
            bot.send_message(user_id, f'Сообщение от администратора:\n{message.text}')
        bot.send_message(
            message.chat.id,
            f'Отправлено {len(tg_users_ids)} сообщений. Копия сообщения:\n {message.text}',
            reply_markup=main_keyboard(message.from_user.id),
        )
    else:
        bot.send_message(
            message.chat.id,
            f'Такой команды не существует. Возврат в основное меню.',
            reply_markup=main_keyboard(message.from_user.id)
        )
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

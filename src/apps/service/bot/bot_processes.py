from telebot import TeleBot
from telebot.types import Message
from apps.service.bot.keyboards import (
    one_time_keyboard_back_to_main,
    one_time_keyboard_send_edit,
    one_time_keyboard_vpn_key_actions,
    main_admin_keyboard,
    bot_message_keyboard,
    one_time_keyboard_back,
)
from apps.service.models import TelegramUsers, OutlineVPNKeys
from apps.service.outline.outline_api import delete_key
from apps.service.processes import (
    get_tg_user_by_,
    get_outline_key_by_id,
    get_all_no_admin_users,
    get_all_vpn_keys_of_user,
    _validate_int,
)


def add_new_vpn_key_to_tg_user_step_1(message: Message, bot: TeleBot):
    """
    Добавление VPN ключа к пользователю. Шаг 1 из 2
    Params:
        message: Message
        bot: TeleBot
    Returns: None
    Exceptions: None
    """
    bot.send_message(
        message.chat.id,
        'Для привязки VPN ключа к пользователю, введите через пробел:\n'
        '- id VPN ключа\n'
        '- логин пользователя TG или его ID\n'
        'Пример: 1 login или 1 123456',
        reply_markup=one_time_keyboard_back_to_main()
    )
    bot.register_next_step_handler(message, add_new_vpn_key_to_tg_user_step_2, bot)


def add_new_vpn_key_to_tg_user_step_2(message: Message, bot: TeleBot):
    """
    Добавление VPN ключа к пользователю. Шаг 2 из 2
    Params:
        message: Message
        bot: TeleBot
    Returns: None
    Exceptions: None
    """
    if 'В основное меню' in message.text:
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_admin_keyboard())
    else:
        data = message.text.split(' ')
        if len(data) == 2:
            outline_vpn_record = get_outline_key_by_id(data[0])
            if isinstance(outline_vpn_record, str):
                bot.send_message(
                    message.chat.id,
                    f'Ошибка. {outline_vpn_record!r}. Повторите ввод данных.'
                )
                bot.register_next_step_handler(message, add_new_vpn_key_to_tg_user_step_2, bot)
            elif isinstance(outline_vpn_record, OutlineVPNKeys):
                if not outline_vpn_record.telegram_user_record:
                    tg_user = get_tg_user_by_(telegram_data=data[1])
                    if isinstance(tg_user, TelegramUsers):
                        outline_vpn_record.add_tg_user(tg_user)
                        bot.send_message(
                            message.chat.id,
                            f'VPN ключ {data[0]!r} привязан к пользователю {tg_user!r}.',
                            reply_markup=main_admin_keyboard())
                    else:
                        bot.send_message(message.chat.id, f'Ошибка. {tg_user!r}. Повторите ввод данных.')
                        bot.register_next_step_handler(message, add_new_vpn_key_to_tg_user_step_2, bot)
                else:
                    bot.send_message(
                        message.chat.id,
                        f'VPN ключ {data[0]!r} уже зарегистрирован за пользователем'
                        f' {outline_vpn_record.telegram_user_record.telegram_id!r}. Повторите ввод данных.'
                    )
                    bot.register_next_step_handler(message, add_new_vpn_key_to_tg_user_step_2, bot)
        else:
            bot.send_message(message.chat.id, f'Некорректные параметры, значений должно быть 2. Повторите ввод данных.')
            bot.register_next_step_handler(message, add_new_vpn_key_to_tg_user_step_2, bot)


def delete_step_1(message: Message, bot: TeleBot):
    """
    Удаление VPN ключа. Шаг 1 из 2
    Params:
        message: Message
        bot: TeleBot
    Returns: None
    Exceptions: None
    """
    bot.send_message(
        message.chat.id,
        'Для удаления VPN ключа введите его ID:\n',
        reply_markup=one_time_keyboard_back_to_main()
    )
    bot.register_next_step_handler(message, delete_step_2, bot)


def delete_step_2(message: Message, bot: TeleBot):
    """
    Удаление VPN ключа. Шаг 2 из 2
    Params:
        message: Message
        bot: TeleBot
    Returns: None
    Exceptions: None
    """
    if 'В основное меню' in message.text:
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_admin_keyboard())
    else:
        outline_vpn_record = get_outline_key_by_id(message.text)
        if isinstance(outline_vpn_record, str):
            bot.send_message(message.chat.id, f'Ошибка.{outline_vpn_record!r}. Повторите ввод данных.')
            bot.register_next_step_handler(message, delete_step_2, bot)
        elif isinstance(outline_vpn_record, OutlineVPNKeys):
            outline_vpn_record.delete()
            msg = delete_key(outline_vpn_record.outline_key_id)
            bot.send_message(
                message.chat.id,
                msg,
                reply_markup=main_admin_keyboard()
            )


def api_key_edit_step_1(message: Message, bot: TeleBot):
    """
    Активация и продление VPN ключа. Шаг 1 из 5
    Params:
        message: Message
        bot: TeleBot
    Returns: None
    Exceptions: None
    """
    bot.send_message(
        message.chat.id,
        'Введите ID VPN ключа, с которым необходимо работать',
        reply_markup=one_time_keyboard_back_to_main()
    )
    bot.register_next_step_handler(message, api_key_edit_step_2, bot)


def api_key_edit_step_2(message: Message, bot: TeleBot):
    """
    Активация и продление VPN ключа. Шаг 2 из 5
    Params:
        message: Message
        bot: TeleBot
    Returns: None
    Exceptions: None
    """
    if 'В основное меню' in message.text:
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_admin_keyboard())
    else:

        outline_vpn_record = get_outline_key_by_id(message.text)
        if isinstance(outline_vpn_record, str):
            bot.send_message(message.chat.id, f'Ошибка.{outline_vpn_record!r}. Повторите ввод данных.')
            bot.register_next_step_handler(message, api_key_edit_step_2, bot)
        elif isinstance(outline_vpn_record, OutlineVPNKeys):
            bot.send_message(
                message.chat.id,
                'Выберите действие:',
                reply_markup=one_time_keyboard_vpn_key_actions(outline_vpn_record.outline_key_active,
                                                               outline_vpn_record.outline_key_traffic_limit)
            )
            bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record)


def api_key_edit_step_3(message: Message, bot: TeleBot, outline_vpn_record: OutlineVPNKeys):
    """
    Активация и продление VPN ключа. Шаг 3 из 5
    Params:
        message: Message
        bot: TeleBot
        outline_vpn_record: OutlineVPNKeys
    Returns: None
    Exceptions: None
    """
    if 'В основное меню' in message.text:
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_admin_keyboard())
    elif 'Изменить срок действия' in message.text:
        bot.send_message(
            message.chat.id,
            'Ведите срок действия ключа в днях. Если указать 0 - ключ будет без ограничения по времени.',
            reply_markup=one_time_keyboard_back()
        )
        bot.register_next_step_handler(message, api_key_edit_step_valid_until, bot, outline_vpn_record)

    elif 'Активировать' in message.text or 'Деактивировать' in message.text:
        key_status = outline_vpn_record.change_active_status()
        outline_vpn_record.refresh_from_db()
        bot.send_message(
            message.chat.id,
            f'VPN ключ {outline_vpn_record.outline_key_id!r}'
            f' {"АКТИВИРОВАН" if key_status else "ДЕАКТИВИРОВАН"},\n',
            reply_markup=one_time_keyboard_vpn_key_actions(outline_vpn_record.outline_key_active,
                                                           outline_vpn_record.outline_key_traffic_limit)
        )
        bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record)

    elif 'Установить лимит трафика' in message.text:
        bot.send_message(
            message.chat.id,
            'Ведите лимит траффика в мегабайтах.',
            reply_markup=one_time_keyboard_back()
        )
        bot.register_next_step_handler(message, api_key_edit_step_traffic_limit, bot, outline_vpn_record)

    elif 'Снять лимит трафика' in message.text:
        outline_vpn_record.del_traffic_limit()
        bot.send_message(
            message.chat.id,
            'Лимит траффика удален',
            reply_markup=one_time_keyboard_vpn_key_actions(outline_vpn_record.outline_key_active,
                                                           outline_vpn_record.outline_key_traffic_limit)
        )
        bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record)

    elif 'Изменить имя' in message.text:
        bot.send_message(
            message.chat.id,
            'В разработке',
            reply_markup=one_time_keyboard_vpn_key_actions(outline_vpn_record.outline_key_active,
                                                           outline_vpn_record.outline_key_traffic_limit)
        )
        bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record)


def api_key_edit_step_valid_until(message: Message, bot: TeleBot, outline_vpn_record: OutlineVPNKeys):
    """
    Активация и продление VPN ключа. Шаг 4 из 5
    Params:
        message: Message
        bot: TeleBot
        outline_vpn_record: OutlineVPNKeys
    Returns: None
    Exceptions: None
    """
    if 'Назад' in message.text:
        bot.send_message(
            message.chat.id,
            'Отмена ввода',
            reply_markup=one_time_keyboard_vpn_key_actions(outline_vpn_record.outline_key_active,
                                                           outline_vpn_record.outline_key_traffic_limit),
        )
        bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record)
    else:
        valid_data = _validate_int(message.text)
        if valid_data:
            valid_until = outline_vpn_record.change_valid_until(valid_data)
            if not valid_until:
                msg = 'без ограничений'
            else:
                msg = f'до {valid_until.strftime("%d-%m-%Y")}'

            outline_vpn_record.refresh_from_db()
            bot.send_message(
                message.chat.id,
                f'На VPN ключ {outline_vpn_record.outline_key_id!r} установлен срок действия {msg}',
                reply_markup=one_time_keyboard_vpn_key_actions(outline_vpn_record.outline_key_active,
                                                               outline_vpn_record.outline_key_traffic_limit)
            )
            bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record)
        else:
            bot.send_message(
                message.chat.id,
                f'Ошибка: {valid_data!r}. Повторите ввод данных.'
            )
            bot.register_next_step_handler(message, api_key_edit_step_valid_until, bot, outline_vpn_record)


def api_key_edit_step_traffic_limit(message: Message, bot: TeleBot, outline_vpn_record: OutlineVPNKeys):
    """
    Активация и продление VPN ключа. Шаг 5 из 5
    Params:
        message: Message
        bot: TeleBot
        outline_vpn_record: OutlineVPNKeys
    Returns: None
    Exceptions: None
    """
    if 'Назад' in message.text:
        bot.send_message(
            message.chat.id,
            'Отмена ввода',
            reply_markup=one_time_keyboard_vpn_key_actions(outline_vpn_record.outline_key_active,
                                                           outline_vpn_record.outline_key_traffic_limit),
        )
        bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record)
    else:
        valid_data = _validate_int(message.text)
        if valid_data:
            outline_vpn_record.add_traffic_limit(valid_data * 1024 * 1024)
            outline_vpn_record.refresh_from_db()
            bot.send_message(
                message.chat.id,
                f'На VPN ключ {outline_vpn_record.outline_key_id!r}'
                f' установлен лимит трафика в размере {message.text} мегабайт',
                reply_markup=one_time_keyboard_vpn_key_actions(outline_vpn_record.outline_key_active,
                                                               outline_vpn_record.outline_key_traffic_limit)
            )
            bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record)
        else:
            bot.send_message(
                message.chat.id,
                f'Ошибка: {valid_data!r}. Повторите ввод данных.'
            )
            bot.register_next_step_handler(message, api_key_edit_step_traffic_limit, bot, outline_vpn_record)


def messages_send_choice_step_1(message: Message, bot: TeleBot):
    bot.send_message(message.chat.id, 'Как отправлять сообщения?', reply_markup=bot_message_keyboard())
    bot.register_next_step_handler(message, messages_send_choice_step_2, bot)


def messages_send_choice_step_2(message: Message, bot: TeleBot):
    if 'В основное меню' in message.text:
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_admin_keyboard())
    elif 'Лично' in message.text:
        personal_message_send_step_1(message, bot)
    elif 'Всем' in message.text:
        all_users_message_send_step_1(message, bot)
    else:
        bot.send_message(
            message.chat.id,
            text='Такой команды не существует.',
            reply_markup=main_admin_keyboard()
        )


def personal_message_send_step_1(message: Message, bot: TeleBot):
    """
    Отправка личного сообщение от лица Бота. Шаг 1 из 3
    Params:
        message: Message
        bot: TeleBot
    Returns: None
    Exceptions: None
    """
    bot.send_message(
        message.chat.id,
        'Укажите TG id пользователя или его логин:\n',
        reply_markup=one_time_keyboard_back()
    )
    bot.register_next_step_handler(message, personal_message_send_step_2, bot)


def personal_message_send_step_2(message: Message, bot: TeleBot):
    """
    Отправка личного сообщение от лица Бота. Шаг 2 из 3
    Params:
        message: Message
        bot: TeleBot
    Returns: None
    Exceptions: None
    """
    if 'Назад' in message.text:
        bot.send_message(
            message.chat.id,
            'Отмена ввода',
            reply_markup=bot_message_keyboard(),
        )
        bot.register_next_step_handler(message, messages_send_choice_step_2, bot)
    else:
        tg_user = get_tg_user_by_(telegram_data=message.text)
        if isinstance(tg_user, TelegramUsers):
            bot.send_message(
                message.chat.id,
                f'Введите сообщение для пользователя:',
                reply_markup=one_time_keyboard_back()
            )
            bot.register_next_step_handler(message, personal_message_send_step_3, bot, tg_user)
        else:
            bot.send_message(message.chat.id, f'Ошибка. {tg_user!r}. Повторите ввод данных.')
            bot.register_next_step_handler(message, personal_message_send_step_2, bot)


def personal_message_send_step_3(message: Message, bot: TeleBot, tg_user: TelegramUsers):
    """
    Отправка личного сообщение от лица Бота. Шаг 3 из 4
    Params:
        message: Message
        bot: TeleBot
    Returns: None
    Exceptions: None
    """
    if 'Назад' in message.text:
        bot.send_message(
            message.chat.id,
            'Отмена ввода',
            reply_markup=bot_message_keyboard(),
        )
        bot.register_next_step_handler(message, messages_send_choice_step_2, bot)
    else:
        msg = message.text
        bot.send_message(
            message.chat.id,
            f'Проверьте сообщение: {msg!r}',
            reply_markup=one_time_keyboard_send_edit()
        )
        bot.register_next_step_handler(message, personal_message_send_step_4, bot, tg_user, msg)


def personal_message_send_step_4(message: Message, bot: TeleBot, tg_user: TelegramUsers, msg: str):
    """
    Отправка личного сообщение от лица Бота. Шаг 4 из 4
    Params:
        message: Message
        bot: TeleBot
        tg_user: TelegramUsers
    Returns: None
    Exceptions: None
    """
    if 'Назад' in message.text:
        bot.send_message(
            message.chat.id,
            'Отмена ввода',
            reply_markup=bot_message_keyboard(),
        )
        bot.register_next_step_handler(message, messages_send_choice_step_2, bot)
    elif 'Редактировать' in message.text:
        bot.send_message(message.chat.id, 'Введите сообщение.', reply_markup=one_time_keyboard_back())
        bot.register_next_step_handler(message, personal_message_send_step_3, bot, tg_user)
    elif 'Отправить' in message.text:
        bot.send_message(tg_user.telegram_id, f'Сообщение от администратора:\n{msg!r}')
        bot.send_message(
            message.chat.id,
            f'Сообщение для пользователя {tg_user.telegram_login!r}, Telegram ID {tg_user.telegram_id!r} отправлено.\n'
            f'Копия сообщения:\n {msg!r}',
            reply_markup=bot_message_keyboard(),
        )
        bot.register_next_step_handler(message, messages_send_choice_step_2, bot)
    else:
        bot.send_message(
            message.chat.id,
            f'Такой команды не существует. Возврат в основное меню',
            reply_markup=main_admin_keyboard()
        )


def all_users_message_send_step_1(message: Message, bot: TeleBot):
    """
    Отправка сообщений от лица Бота ВСЕМ пользователям, кроме администраторов. Шаг 1 из 3
    Params:
        message: Message
        bot: TeleBot
    Returns: None
    Exceptions: None
    """
    bot.send_message(
        message.chat.id,
        'Введите сообщение для всех пользователей\n',
        reply_markup=one_time_keyboard_back()
    )
    bot.register_next_step_handler(message, all_users_message_send_step_2, bot)


def all_users_message_send_step_2(message: Message, bot: TeleBot):
    """
    Отправка сообщений от лица Бота ВСЕМ пользователям, кроме администраторов. Шаг 2 из 3
    Params:
        message: Message
        bot: TeleBot
    Returns: None
    Exceptions: None
    """
    if 'Назад' in message.text:
        bot.send_message(
            message.chat.id,
            'Отмена ввода',
            reply_markup=bot_message_keyboard(),
        )
        bot.register_next_step_handler(message, messages_send_choice_step_2, bot)
    else:
        msg = message.text
        bot.send_message(
            message.chat.id,
            f'Проверьте сообщение: {msg!r}',
            reply_markup=one_time_keyboard_send_edit()
        )
        bot.register_next_step_handler(message, all_users_message_send_step_3, bot, msg)


def all_users_message_send_step_3(message: Message, bot: TeleBot, msg: str):
    """
    Отправка сообщений от лица Бота ВСЕМ пользователям, кроме администраторов. Шаг 3 из 3
    Params:
        message: Message
        bot: TeleBot
        msg: str
    Returns: None
    Exceptions: None
    """
    if 'Назад' in message.text:
        bot.send_message(
            message.chat.id,
            'Отмена ввода',
            reply_markup=bot_message_keyboard(),
        )
        bot.register_next_step_handler(message, messages_send_choice_step_2, bot)
    elif 'Редактировать' in message.text:
        bot.send_message(message.chat.id, 'Введите сообщение.', reply_markup=one_time_keyboard_back())
        bot.register_next_step_handler(message, all_users_message_send_step_2, bot)
    elif 'Отправить' in message.text:
        tg_users_ids = get_all_no_admin_users()
        for user_id in tg_users_ids:
            bot.send_message(user_id, f'Сообщение от администратора:\n{msg!r}')
        bot.send_message(
            message.chat.id,
            f'Отправлено {len(tg_users_ids)} сообщений. Копия сообщения:\n {msg!r}',
            reply_markup=bot_message_keyboard(),
        )
        bot.register_next_step_handler(message, messages_send_choice_step_2, bot)
    else:
        bot.send_message(
            message.chat.id,
            f'Такой команды не существует. Возврат в основное меню',
            reply_markup=main_admin_keyboard()
        )


def user_vpn_keys_list_step_1(message: Message, bot: TeleBot):
    """
    Получение списка VPN ключей пользователя. Шаг 1 из 2
    Params:
        message: Message
        bot: TeleBot
    Returns: None
    Exceptions: None
    """
    bot.send_message(
        message.chat.id,
        'Для получения списка VPN ключей пользователя введите его Telegram ID или Telegram Login:\n',
        reply_markup=one_time_keyboard_back_to_main()
    )
    bot.register_next_step_handler(message, user_vpn_keys_list_step_2, bot)


def user_vpn_keys_list_step_2(message: Message, bot: TeleBot):
    """
    Получение списка VPN ключей пользователя. Шаг 2 из 2
    Params:
        message: Message
        bot: TeleBot
    Returns: None
    Exceptions: None
    """
    if 'В основное меню' in message.text:
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_admin_keyboard())
    else:
        vpn_keys = get_all_vpn_keys_of_user(message.text)
        if isinstance(vpn_keys, str):
            bot.send_message(
                message.chat.id,
                f'{vpn_keys}, повторите ввод',
            )
            bot.register_next_step_handler(message, user_vpn_keys_list_step_2, bot)
        else:
            bot.send_message(
                message.chat.id,
                '\n'.join(vpn_keys) if vpn_keys else 'Ключи отсутствуют',
                reply_markup=main_admin_keyboard(),
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
#         bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=admin_keyboard())
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
#         bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=admin_keyboard())
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
#         bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=admin_keyboard())
#     else:
#         bot.send_message(message.chat.id, name_add(client, key_id, message.text))
#         bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=admin_keyboard())
#

import requests
from telebot import TeleBot

from bot_exceptions import SERVER_EXCEPTION
from config_loader import CONFIG
from telebot.types import Message, User

# from telegram_client_bot.keyboards import (
#     one_time_keyboard_back_to_main,
#     one_time_keyboard_send_edit,
#     vpn_key_edit_actions_keyboard,
#     main_admin_keyboard,
#     bot_message_keyboard,
#     one_time_keyboard_back,
#     delete_keyboard,
# )
# from apps.outline_vpn_admin.models import TelegramUsers, OutlineVPNKeys
# from apps.outline_vpn_admin.processes import (
#     get_tg_user_by_,
#     get_outline_key_by_id,
#     get_all_no_admin_users,
#     get_all_vpn_keys_of_user,
#     validate_int,
#     create_new_key,
#     add_traffic_limit,
#     del_traffic_limit,
#     del_outline_vpn_key,
#     change_outline_vpn_key_name,
# )

API_CREDS_USERNAME = CONFIG['bot']['api']['username']
API_CREDS_PASSWORD = CONFIG['bot']['api']['password']
API_URL = CONFIG['bot']['api']['url']
API_URIS = CONFIG['bot']['api']['uris']
BOT_NAME = CONFIG['bot']['name']
ADMINS = CONFIG['bot']['admin_users']


def get_auth_api_headers():
    response = requests.post(
        f'{API_URL}{API_URIS["get_auth_token"]}',
        data={
            'username': API_CREDS_USERNAME,
            'password': API_CREDS_PASSWORD
        },
        allow_redirects=True,
    )
    return {'Authorization': f'Token  {response.json()["token"]}'}


def send_alert_to_admins(bot: TeleBot, user: User, text: str) -> None:
    """Функция отправки сообщений всем администратора"""
    for admin_id in ADMINS:
        bot.send_message(
            admin_id,
            text=f'ОШИБКА У ПОЛЬЗОВАТЕЛЯ:'
                 f'Пользователь:\n'
                 f'ID - {user.id!r}\n'
                 f'Логин - {user.username!r}\n'
                 f'ФИО - {user.full_name!r}\n'
                 f'Произошла ошибка:\n{text}',
        )


def send_msg_to_admins(bot: TeleBot, user: User, text: str, message: Message) -> None:
    """Функция отправки сообщений всем администратора"""
    for admin_id in ADMINS:
        bot.send_message(
            admin_id,
            text=f'Пользователь:\n'
                 f'ID - {user.id!r}\n'
                 f'Логин - {user.username!r}\n'
                 f'ФИО - {user.full_name!r}\n'
                 f'{text}',
        )
        bot.forward_message(admin_id, message.chat.id, message.message_id)


def add_or_update_user(user: User) -> None:

    headers = get_auth_api_headers()
    to_send = {
        'transport_name': BOT_NAME,
        'credentials': user.to_dict()
    }

    response = requests.post(
        f'{API_URL}{API_URIS["creat_or_update_contact"]}',
        headers=headers,
        json=to_send,
        allow_redirects=True,
    )
    # print(response.json())


def get_vpn_keys(user: User) -> list or str:
    headers = get_auth_api_headers()
    to_send = {
        'transport_name': BOT_NAME,
        'messenger_id': user.id
    }
    response = requests.get(
        f'{API_URL}{API_URIS["get_client_tokens"].format(**to_send)}',
        headers=headers,
        allow_redirects=True,
    )
    if response.status_code == 200:
        return response.json()['tokens'], ''

    return SERVER_EXCEPTION, f'{response.status_code=!r}\n{response.json()=!r}'
    # print(response.json())

# def bot_create_key(server_name: str, tg_user_id: int = None):
#     vpn_key = create_new_key(server_name)
#     demo_traffic_limit = None
#     if tg_user_id:
#         vpn_key.add_tg_user(get_tg_user_by_(telegram_data=tg_user_id))
#         vpn_key.change_active_status()
#         vpn_key.change_valid_until(7)
#         demo_traffic_limit = 1024 * 1024 * 1024
#     add_traffic_limit(server_name, vpn_key, demo_traffic_limit)
#     return vpn_key
#
#
# def api_key_edit_step_1(message: Message, bot: TeleBot, vpn_server_name: str):
#     """
#     Редактирование ключа.
#      Получение ID VPN ключа от пользователя. Шаг 1 из 3
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#     Returns: None
#     Exceptions: None
#     """
#     bot.send_message(
#         message.chat.id,
#         'Введите ID VPN ключа, с которым необходимо работать',
#         reply_markup=one_time_keyboard_back_to_main()
#     )
#     bot.register_next_step_handler(message, api_key_edit_step_2, bot, vpn_server_name)
#
#
# def api_key_edit_step_2(message: Message, bot: TeleBot, vpn_server_name: str):
#     """
#     Редактирование ключа.
#      Валидация ID VPN ключа и получение OutlineVPNKeys для дальнейшей обработки. Шаг 2 из 3
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#     Returns: None
#     Exceptions: None
#     """
#     if 'В основное меню' in message.text:
#         bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_admin_keyboard())
#     else:
#         outline_vpn_record = get_outline_key_by_id(message.text)
#         if isinstance(outline_vpn_record, str):
#             bot.send_message(message.chat.id, f'Ошибка.{outline_vpn_record!r}. Повторите ввод данных.')
#             bot.register_next_step_handler(message, api_key_edit_step_2, bot, vpn_server_name)
#         elif isinstance(outline_vpn_record, OutlineVPNKeys):
#             bot.send_message(
#                 message.chat.id,
#                 'Выберите действие:',
#                 reply_markup=vpn_key_edit_actions_keyboard(outline_vpn_record.outline_key_active,
#                                                            outline_vpn_record.outline_key_traffic_limit)
#             )
#             bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record, vpn_server_name)
#
#
# def api_key_edit_step_3(message: Message, bot: TeleBot, outline_vpn_record: OutlineVPNKeys, vpn_server_name: str):
#     """
#     Редактирование VPN ключа.
#     Меню выбора действий над ключом.
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#         outline_vpn_record: OutlineVPNKeys
#     Returns: None
#     Exceptions: None
#     """
#     if 'В основное меню' in message.text:
#         bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_admin_keyboard())
#     elif 'Изменить срок действия' in message.text:
#         bot.send_message(
#             message.chat.id,
#             'Ведите срок действия ключа в днях. Если указать 0 - ключ будет без ограничения по времени.',
#             reply_markup=one_time_keyboard_back()
#         )
#         bot.register_next_step_handler(message, api_key_edit_step_valid_until, bot, outline_vpn_record, vpn_server_name)
#
#     elif 'Активировать' in message.text or 'Деактивировать' in message.text:
#         key_status = outline_vpn_record.change_active_status()
#         outline_vpn_record.refresh_from_db()
#         bot.send_message(
#             message.chat.id,
#             f'VPN ключ {outline_vpn_record.outline_key_id!r}'
#             f' {"АКТИВИРОВАН" if key_status else "ДЕАКТИВИРОВАН"},\n',
#             reply_markup=vpn_key_edit_actions_keyboard(outline_vpn_record.outline_key_active,
#                                                        outline_vpn_record.outline_key_traffic_limit)
#         )
#         bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record, vpn_server_name)
#
#     elif 'Установить лимит трафика' in message.text:
#         bot.send_message(
#             message.chat.id,
#             'Ведите лимит траффика в мегабайтах.',
#             reply_markup=one_time_keyboard_back()
#         )
#         bot.register_next_step_handler(
#             message,
#             api_key_edit_step_traffic_limit,
#             bot,
#             outline_vpn_record,
#             vpn_server_name,
#         )
#
#     elif 'Снять лимит трафика' in message.text:
#         del_traffic_limit(vpn_server_name, outline_vpn_record)
#         bot.send_message(
#             message.chat.id,
#             'Лимит траффика удален',
#             reply_markup=vpn_key_edit_actions_keyboard(outline_vpn_record.outline_key_active,
#                                                        outline_vpn_record.outline_key_traffic_limit)
#         )
#         bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record, vpn_server_name)
#
#     elif 'Изменить имя' in message.text:
#         bot.send_message(message.chat.id, 'Введите Имя ключа.', reply_markup=one_time_keyboard_back())
#         bot.register_next_step_handler(message, api_key_edit_change_name, bot, outline_vpn_record, vpn_server_name)
#
#     elif 'Удалить ключ' in message.text:
#         bot.send_message(message.chat.id, 'Вы уверены что хотите удалить данный ключ?', reply_markup=delete_keyboard())
#         bot.register_next_step_handler(
#             message,
#             api_key_edit_step_delete_vpn_key,
#             bot,
#             outline_vpn_record,
#             vpn_server_name,
#         )
#
#     elif 'Привязать ключ к пользователю' in message.text:
#         bot.send_message(
#             message.chat.id,
#             'Ведите логин пользователя Telegram или его ID',
#             reply_markup=one_time_keyboard_back()
#         )
#         bot.register_next_step_handler(
#             message,
#             api_key_edit_step_add_tg_user_to_vpn_key,
#             bot,
#             outline_vpn_record,
#             vpn_server_name
#         )
#
#     else:
#         bot.send_message(
#             message.chat.id,
#             text='Такой команды не существует.',
#             reply_markup=vpn_key_edit_actions_keyboard(outline_vpn_record.outline_key_active,
#                                                        outline_vpn_record.outline_key_traffic_limit)
#         )
#         bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record, vpn_server_name)
#
#
# def api_key_edit_change_name(
#     message: Message,
#     bot: TeleBot,
#     outline_vpn_record: OutlineVPNKeys,
#     vpn_server_name: str
# ):
#     if 'Назад' in message.text:
#         bot.send_message(
#             message.chat.id,
#             'Отмена ввода',
#             reply_markup=vpn_key_edit_actions_keyboard(outline_vpn_record.outline_key_active,
#                                                        outline_vpn_record.outline_key_traffic_limit),
#         )
#         bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record, vpn_server_name)
#     else:
#         change_outline_vpn_key_name(vpn_server_name, outline_vpn_record, message.text)
#         bot.send_message(
#             message.chat.id,
#             f'Имя ключа изменено на:\n{message.text!r}',
#             reply_markup=vpn_key_edit_actions_keyboard(
#                 outline_vpn_record.outline_key_active,
#                 outline_vpn_record.outline_key_traffic_limit
#             ),
#         )
#         bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record, vpn_server_name)
#
#
# def api_key_edit_step_delete_vpn_key(
#     message: Message,
#     bot: TeleBot,
#     outline_vpn_record: OutlineVPNKeys,
#     vpn_server_name: str
# ):
#     """
#     Редактирование VPN ключа.
#         Удаление VPN ключа
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#     Returns: None
#     Exceptions: None
#     """
#     if 'Назад' in message.text:
#         bot.send_message(
#             message.chat.id,
#             'Отмена ввода',
#             reply_markup=vpn_key_edit_actions_keyboard(outline_vpn_record.outline_key_active,
#                                                        outline_vpn_record.outline_key_traffic_limit),
#         )
#         bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record, vpn_server_name)
#
#     elif 'Удалить' in message.text:
#         response = del_outline_vpn_key(vpn_server_name, outline_vpn_record)
#         if response:
#             bot.send_message(
#                 message.chat.id,
#                 'Ключ удален. Возврат в основное меню.',
#                 reply_markup=main_admin_keyboard()
#             )
#         else:
#             bot.send_message(
#                 message.chat.id,
#                 'Ошибка удаления ключа. Повторите выбор или вернитесь в предыдущее меню.',
#                 reply_markup=delete_keyboard()
#             )
#             bot.register_next_step_handler(
#                 message,
#                 api_key_edit_step_delete_vpn_key,
#                 bot,
#                 outline_vpn_record,
#                 vpn_server_name,
#             )
#     else:
#         bot.send_message(
#             message.chat.id,
#             text='Такой команды не существует. Выберите действие',
#             reply_markup=delete_keyboard()
#         )
#         bot.register_next_step_handler(
#             message,
#             api_key_edit_step_delete_vpn_key,
#             bot,
#             outline_vpn_record,
#             vpn_server_name,
#         )
#
#
# def api_key_edit_step_add_tg_user_to_vpn_key(
#     message: Message,
#     bot: TeleBot,
#     outline_vpn_record: OutlineVPNKeys,
#     vpn_server_name: str
# ):
#     """
#     Редактирование VPN ключа.
#         Добавление VPN ключа к пользователю.
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#     Returns: None
#     Exceptions: None
#     """
#     if 'Назад' in message.text:
#         bot.send_message(
#             message.chat.id,
#             'Отмена ввода',
#             reply_markup=vpn_key_edit_actions_keyboard(outline_vpn_record.outline_key_active,
#                                                        outline_vpn_record.outline_key_traffic_limit),
#         )
#         bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record, vpn_server_name)
#     else:
#         if not outline_vpn_record.telegram_user_record:
#             tg_user = get_tg_user_by_(telegram_data=message.text)
#             if isinstance(tg_user, TelegramUsers):
#                 outline_vpn_record.add_tg_user(tg_user)
#                 bot.send_message(
#                     message.chat.id,
#                     f'VPN ключ {outline_vpn_record.outline_key_id!r} привязан к пользователю {tg_user!r}.',
#                     reply_markup=vpn_key_edit_actions_keyboard(
#                         outline_vpn_record.outline_key_active,
#                         outline_vpn_record.outline_key_traffic_limit
#                     )
#                 )
#                 bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record, vpn_server_name)
#             else:
#                 bot.send_message(message.chat.id, f'Ошибка. {tg_user!r}. Повторите ввод данных.')
#                 bot.register_next_step_handler(
#                     message,
#                     api_key_edit_step_add_tg_user_to_vpn_key,
#                     bot,
#                     outline_vpn_record,
#                     vpn_server_name,
#                 )
#         else:
#             bot.send_message(
#                 message.chat.id,
#                 f'VPN ключ {outline_vpn_record.outline_key_id!r} уже зарегистрирован за пользователем'
#                 f' {outline_vpn_record.telegram_user_record.telegram_id!r}. Отмена ввода.',
#                 reply_markup=vpn_key_edit_actions_keyboard(
#                     outline_vpn_record.outline_key_active,
#                     outline_vpn_record.outline_key_traffic_limit,
#                 ),
#             )
#             bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record, vpn_server_name)
#
#
# def api_key_edit_step_valid_until(
#     message: Message,
#     bot: TeleBot,
#     outline_vpn_record: OutlineVPNKeys,
#     vpn_server_name: str
# ):
#     """
#     Редактирование VPN ключа.
#         Установка срока действия ключа.
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#         outline_vpn_record: OutlineVPNKeys
#     Returns: None
#     Exceptions: None
#     """
#     if 'Назад' in message.text:
#         bot.send_message(
#             message.chat.id,
#             'Отмена ввода',
#             reply_markup=vpn_key_edit_actions_keyboard(outline_vpn_record.outline_key_active,
#                                                        outline_vpn_record.outline_key_traffic_limit),
#         )
#         bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record, vpn_server_name)
#     else:
#         valid_data = validate_int(message.text)
#         if isinstance(valid_data, int):
#             valid_until = outline_vpn_record.change_valid_until(valid_data)
#             if not valid_until:
#                 msg = 'без ограничений'
#             else:
#                 msg = f'до {valid_until.strftime("%d-%m-%Y")}'
#
#             outline_vpn_record.refresh_from_db()
#             bot.send_message(
#                 message.chat.id,
#                 f'На VPN ключ {outline_vpn_record.outline_key_id!r} установлен срок действия {msg}',
#                 reply_markup=vpn_key_edit_actions_keyboard(outline_vpn_record.outline_key_active,
#                                                            outline_vpn_record.outline_key_traffic_limit)
#             )
#             bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record, vpn_server_name)
#         else:
#             bot.send_message(
#                 message.chat.id,
#                 f'Ошибка: {valid_data!r}. Повторите ввод данных.'
#             )
#             bot.register_next_step_handler(message, api_key_edit_step_valid_until, bot, outline_vpn_record,
#                                            vpn_server_name)
#
#
# def api_key_edit_step_traffic_limit(
#     message: Message,
#     bot: TeleBot,
#     outline_vpn_record: OutlineVPNKeys,
#     vpn_server_name: str
# ):
#     """
#     Редактирование VPN ключа.
#         Установка лимита трафика
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#         outline_vpn_record: OutlineVPNKeys
#     Returns: None
#     Exceptions: None
#     """
#     if 'Назад' in message.text:
#         bot.send_message(
#             message.chat.id,
#             'Отмена ввода',
#             reply_markup=vpn_key_edit_actions_keyboard(outline_vpn_record.outline_key_active,
#                                                        outline_vpn_record.outline_key_traffic_limit),
#         )
#         bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record, vpn_server_name)
#     else:
#         valid_data = validate_int(message.text)
#         if isinstance(valid_data, int):
#             add_traffic_limit(vpn_server_name, outline_vpn_record, valid_data * 1024 * 1024)
#             outline_vpn_record.refresh_from_db()
#             bot.send_message(
#                 message.chat.id,
#                 f'На VPN ключ {outline_vpn_record.outline_key_id!r}'
#                 f' установлен лимит трафика в размере {message.text} мегабайт',
#                 reply_markup=vpn_key_edit_actions_keyboard(outline_vpn_record.outline_key_active,
#                                                            outline_vpn_record.outline_key_traffic_limit)
#             )
#             bot.register_next_step_handler(message, api_key_edit_step_3, bot, outline_vpn_record, vpn_server_name)
#         else:
#             bot.send_message(
#                 message.chat.id,
#                 f'Ошибка: {valid_data!r}. Повторите ввод данных.'
#             )
#             bot.register_next_step_handler(message, api_key_edit_step_traffic_limit, bot, outline_vpn_record,
#                                            vpn_server_name)
#
#
# def messages_send_choice_step_1(message: Message, bot: TeleBot):
#     bot.send_message(message.chat.id, 'Как отправлять сообщения?', reply_markup=bot_message_keyboard())
#     bot.register_next_step_handler(message, messages_send_choice_step_2, bot)
#
#
# def messages_send_choice_step_2(message: Message, bot: TeleBot):
#     if 'В основное меню' in message.text:
#         bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_admin_keyboard())
#     elif 'Лично' in message.text:
#         personal_message_send_step_1(message, bot)
#     elif 'Всем' in message.text:
#         all_users_message_send_step_1(message, bot)
#     else:
#         bot.send_message(
#             message.chat.id,
#             text='Такой команды не существует.',
#             reply_markup=main_admin_keyboard()
#         )
#
#
# def personal_message_send_step_1(message: Message, bot: TeleBot):
#     """
#     Отправка личного сообщение от лица Бота. Шаг 1 из 3
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#     Returns: None
#     Exceptions: None
#     """
#     bot.send_message(
#         message.chat.id,
#         'Укажите TG id пользователя или его логин:\n',
#         reply_markup=one_time_keyboard_back()
#     )
#     bot.register_next_step_handler(message, personal_message_send_step_2, bot)
#
#
# def personal_message_send_step_2(message: Message, bot: TeleBot):
#     """
#     Отправка личного сообщение от лица Бота. Шаг 2 из 3
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#     Returns: None
#     Exceptions: None
#     """
#     if 'Назад' in message.text:
#         bot.send_message(
#             message.chat.id,
#             'Отмена ввода',
#             reply_markup=bot_message_keyboard(),
#         )
#         bot.register_next_step_handler(message, messages_send_choice_step_2, bot)
#     else:
#         tg_user = get_tg_user_by_(telegram_data=message.text)
#         if isinstance(tg_user, TelegramUsers):
#             bot.send_message(
#                 message.chat.id,
#                 f'Введите сообщение для пользователя:',
#                 reply_markup=one_time_keyboard_back()
#             )
#             bot.register_next_step_handler(message, personal_message_send_step_3, bot, tg_user)
#         else:
#             bot.send_message(message.chat.id, f'Ошибка. {tg_user!r}. Повторите ввод данных.')
#             bot.register_next_step_handler(message, personal_message_send_step_2, bot)
#
#
# def personal_message_send_step_3(message: Message, bot: TeleBot, tg_user: TelegramUsers):
#     """
#     Отправка личного сообщение от лица Бота. Шаг 3 из 4
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#     Returns: None
#     Exceptions: None
#     """
#     if 'Назад' in message.text:
#         bot.send_message(
#             message.chat.id,
#             'Отмена ввода',
#             reply_markup=bot_message_keyboard(),
#         )
#         bot.register_next_step_handler(message, messages_send_choice_step_2, bot)
#     else:
#         msg = message.text
#         bot.send_message(
#             message.chat.id,
#             f'Проверьте сообщение: {msg!r}',
#             reply_markup=one_time_keyboard_send_edit()
#         )
#         bot.register_next_step_handler(message, personal_message_send_step_4, bot, tg_user, msg)
#
#
# def personal_message_send_step_4(message: Message, bot: TeleBot, tg_user: TelegramUsers, msg: str):
#     """
#     Отправка личного сообщение от лица Бота. Шаг 4 из 4
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#         tg_user: TelegramUsers
#     Returns: None
#     Exceptions: None
#     """
#     if 'Назад' in message.text:
#         bot.send_message(
#             message.chat.id,
#             'Отмена ввода',
#             reply_markup=bot_message_keyboard(),
#         )
#         bot.register_next_step_handler(message, messages_send_choice_step_2, bot)
#     elif 'Редактировать' in message.text:
#         bot.send_message(message.chat.id, 'Введите сообщение.', reply_markup=one_time_keyboard_back())
#         bot.register_next_step_handler(message, personal_message_send_step_3, bot, tg_user)
#     elif 'Отправить' in message.text:
#         bot.send_message(tg_user.telegram_id, f'Сообщение от администратора:\n{msg!r}')
#         bot.send_message(
#             message.chat.id,
#             f'Сообщение для пользователя {tg_user.telegram_login!r}, Telegram ID {tg_user.telegram_id!r} отправлено.\n'
#             f'Копия сообщения:\n {msg!r}',
#             reply_markup=bot_message_keyboard(),
#         )
#         bot.register_next_step_handler(message, messages_send_choice_step_2, bot)
#     else:
#         bot.send_message(
#             message.chat.id,
#             f'Такой команды не существует. Возврат в основное меню',
#             reply_markup=main_admin_keyboard()
#         )
#
#
# def all_users_message_send_step_1(message: Message, bot: TeleBot):
#     """
#     Отправка сообщений от лица Бота ВСЕМ пользователям, кроме администраторов. Шаг 1 из 3
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#     Returns: None
#     Exceptions: None
#     """
#     bot.send_message(
#         message.chat.id,
#         'Введите сообщение для всех пользователей\n',
#         reply_markup=one_time_keyboard_back()
#     )
#     bot.register_next_step_handler(message, all_users_message_send_step_2, bot)
#
#
# def all_users_message_send_step_2(message: Message, bot: TeleBot):
#     """
#     Отправка сообщений от лица Бота ВСЕМ пользователям, кроме администраторов. Шаг 2 из 3
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#     Returns: None
#     Exceptions: None
#     """
#     if 'Назад' in message.text:
#         bot.send_message(
#             message.chat.id,
#             'Отмена ввода',
#             reply_markup=bot_message_keyboard(),
#         )
#         bot.register_next_step_handler(message, messages_send_choice_step_2, bot)
#     else:
#         msg = message.text
#         bot.send_message(
#             message.chat.id,
#             f'Проверьте сообщение: {msg!r}',
#             reply_markup=one_time_keyboard_send_edit()
#         )
#         bot.register_next_step_handler(message, all_users_message_send_step_3, bot, msg)
#
#
# def all_users_message_send_step_3(message: Message, bot: TeleBot, msg: str):
#     """
#     Отправка сообщений от лица Бота ВСЕМ пользователям, кроме администраторов. Шаг 3 из 3
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#         msg: str
#     Returns: None
#     Exceptions: None
#     """
#     if 'Назад' in message.text:
#         bot.send_message(
#             message.chat.id,
#             'Отмена ввода',
#             reply_markup=bot_message_keyboard(),
#         )
#         bot.register_next_step_handler(message, messages_send_choice_step_2, bot)
#     elif 'Редактировать' in message.text:
#         bot.send_message(message.chat.id, 'Введите сообщение.', reply_markup=one_time_keyboard_back())
#         bot.register_next_step_handler(message, all_users_message_send_step_2, bot)
#     elif 'Отправить' in message.text:
#         tg_users_ids = get_all_no_admin_users()
#         for user_id in tg_users_ids:
#             bot.send_message(user_id, f'Сообщение от администратора:\n{msg!r}')
#         bot.send_message(
#             message.chat.id,
#             f'Отправлено {len(tg_users_ids)} сообщений. Копия сообщения:\n {msg!r}',
#             reply_markup=bot_message_keyboard(),
#         )
#         bot.register_next_step_handler(message, messages_send_choice_step_2, bot)
#     else:
#         bot.send_message(
#             message.chat.id,
#             f'Такой команды не существует. Возврат в основное меню',
#             reply_markup=main_admin_keyboard()
#         )
#
#
# def user_vpn_keys_list_step_1(message: Message, bot: TeleBot):
#     """
#     Получение списка VPN ключей пользователя. Шаг 1 из 2
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#     Returns: None
#     Exceptions: None
#     """
#     bot.send_message(
#         message.chat.id,
#         'Для получения списка VPN ключей пользователя введите его Telegram ID или Telegram Login:\n',
#         reply_markup=one_time_keyboard_back_to_main()
#     )
#     bot.register_next_step_handler(message, user_vpn_keys_list_step_2, bot)
#
#
# def user_vpn_keys_list_step_2(message: Message, bot: TeleBot):
#     """
#     Получение списка VPN ключей пользователя. Шаг 2 из 2
#     Params:
#         message: Message
#         telegram_client_bot: TeleBot
#     Returns: None
#     Exceptions: None
#     """
#     if 'В основное меню' in message.text:
#         bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_admin_keyboard())
#     else:
#         vpn_keys = get_all_vpn_keys_of_user(message.text)
#         if isinstance(vpn_keys, str):
#             bot.send_message(
#                 message.chat.id,
#                 f'{vpn_keys}, повторите ввод',
#             )
#             bot.register_next_step_handler(message, user_vpn_keys_list_step_2, bot)
#         else:
#             bot.send_message(
#                 message.chat.id,
#                 '\n'.join(vpn_keys) if vpn_keys else 'Ключи отсутствуют',
#                 reply_markup=main_admin_keyboard(),
#             )

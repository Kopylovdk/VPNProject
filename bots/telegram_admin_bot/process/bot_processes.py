import requests
import logging
import os

from requests import Response
from telebot import TeleBot, types
from telebot.apihelper import ApiTelegramException
from exceptions.bot_exceptions import SERVER_EXCEPTION
from process.config_loader import CONFIG
from telebot.types import Message, User
from functools import lru_cache
from process.keyboards import (
    main_keyboard,
    generate_action_keyboard,
    back_to_main_menu_keyboard,
)

log = logging.getLogger(__name__)

API_CREDS_USERNAME = os.environ.get('USERNAME')
API_CREDS_PASSWORD = os.environ.get('PASSWORD')
API_URL = CONFIG['bot']['api']['url']
API_URIS = CONFIG['bot']['api']['uris']
BOT_NAME = CONFIG['bot']['name']
TECH_ADMIN = CONFIG['bot']['tech_admin']
MANAGERS = CONFIG['bot']['managers']





def check_int(data: str) -> int or str:
    try:
        int(data)
        return True
    except ValueError:
        return False


def health_check() -> Response:
    url = f'{API_URL}{API_URIS["health"]}'
    response = requests.get(url, allow_redirects=True)
    return response


@lru_cache(maxsize=None)
def get_auth_api_headers(bot: TeleBot) -> dict:
    response = requests.post(
        f'{API_URL}{API_URIS["get_auth_token"]}',
        data={
            'username': API_CREDS_USERNAME,
            'password': API_CREDS_PASSWORD
        },
        allow_redirects=True,
    )
    log.info(f'{API_CREDS_USERNAME=}, {API_CREDS_PASSWORD=}')
    if response.status_code == 200:
        log.info('get_auth_api_headers executed')
        return {'Authorization': f'Token  {response.json()["token"]}'}
    else:
        send_alert_to_admins(bot=bot, response=response)


@lru_cache(maxsize=None)
def get_tariffs(bot: TeleBot) -> list:
    response = requests.get(
        f'{API_URL}{API_URIS["get_tariffs"]}',
        headers=get_auth_api_headers(bot=bot),
        allow_redirects=True,
    )
    if response.status_code == 200:
        log.info(f'get_tariffs executed')
        tariffs = response.json()["tariffs"]
        for i, tariff in enumerate(tariffs):
            if tariff['is_tech']:
                del tariffs[i]
        return tariffs
    else:
        send_alert_to_admins(bot=bot, response=response)


@lru_cache(maxsize=None)
def get_vpn_servers(bot: TeleBot) -> list:
    response = requests.get(
        f'{API_URL}{API_URIS["get_vpn_servers"]}',
        headers=get_auth_api_headers(bot=bot),
        allow_redirects=True,
    )
    if response.status_code == 200:
        log.info('get_vpn_servers executed')
        return response.json()["vpn_servers"]
    else:
        send_alert_to_admins(bot=bot, response=response)


def get_client(bot: TeleBot, messenger_id: int) -> dict:
    data = {
        'transport_name': BOT_NAME,
        'messenger_id': messenger_id,
    }
    response = requests.get(
        f'{API_URL}{API_URIS["get_contact"].format(**data)}',
        headers=get_auth_api_headers(bot=bot),
        allow_redirects=True,
    )
    status_code = response.status_code
    response_json = response.json()
    if status_code == 200:
        return response.json()
    elif status_code in [404] and "User does not exist" in response_json['details']:
        bot.send_message(
            messenger_id,
            "Вы не зарегистрированы.\nПожалуйста, пройдите регистрацию, нажав на соответствующую кнопку в Меню",
            reply_markup=main_keyboard()
        )
    else:
        send_alert_to_admins(bot=bot, response=response)


def send_alert_to_admins(bot: TeleBot, response: Response, user: User = None) -> None:
    """Функция отправки сообщений всем администратора"""
    if user:
        text = f'ОШИБКА У КЛИЕНТА:\n' \
               f'Пользователь:\n' \
               f'ID - {user.id!r}\n' \
               f'Логин - {user.username!r}\n' \
               f'ФИО - {user.full_name!r}\n' \
               f'Произошла ошибка:\n' \
               f'Status_code = {response.status_code!r}\n' \
               f'Response = {response.json()}'
        log.error(f'{response.json()=!r}, {text!r}')
    else:
        text = f'ОШИБКА ПОДКЛЮЧЕНИЯ К БЭКУ:' \
               f' Status_code = {response.status_code!r},' \
               f' url = {response.url!r},' \
               f' headers = {response.headers}'
        log.error(f'{text!r}')

    for admin_id in TECH_ADMIN:
        bot.send_message(admin_id, text=text)


def send_msg_to_managers(bot: TeleBot, text: str, message: Message) -> None:
    """Функция отправки сообщений всем менеджерам"""
    response = get_client(bot, message.from_user.id)
    for manager_id in MANAGERS:
        try:
            bot.send_message(
                manager_id,
                text=f'Пользователь:\n'
                     f'ID - {message.from_user.id!r}\n'
                     f'Логин - {message.from_user.username!r}\n'
                     f'ФИО - {message.from_user.full_name!r}\n'
                     f'Номер телефона - {response["user_info"]["contact"]["phone_number"]!r}\n'
                     f'{text}',
            )
        except ApiTelegramException:
            continue
        # bot.forward_message(manager_id, message.chat.id, message.message_id)


def add_or_update_user(bot: TeleBot, message: Message) -> None:
    credentials = message.from_user.to_dict()
    credentials['phone_number'] = message.contact.phone_number

    to_send = {
        'transport_name': BOT_NAME,
        'credentials': credentials,
    }
    response = requests.post(
        f'{API_URL}{API_URIS["creat_or_update_contact"]}',
        headers=get_auth_api_headers(bot=bot),
        json=to_send,
        allow_redirects=True,
    )
    if response.status_code in [200, 201]:
        json_response = response.json()
        bot.send_message(
            message.chat.id,
            'Вы успешно зарегистрированы. Теперь Вам доступен весь функционал.',
            reply_markup=main_keyboard(),
        )
        log.info(f'{json_response["details"]}:\n{json_response["user_info"]}')
    else:
        bot.send_message(message.chat.id, SERVER_EXCEPTION, reply_markup=main_keyboard())
        send_alert_to_admins(bot, response, message.from_user)
        log.error(f'add or update error {response}, {message}')


def get_vpn_keys(bot: TeleBot, user: User) -> None:
    user_id = user.id
    send_wait_message_to_user(bot, user_id)
    to_send = {
        'transport_name': BOT_NAME,
        'messenger_id': user.id
    }
    response = requests.get(
        f'{API_URL}{API_URIS["get_client_tokens"].format(**to_send)}',
        headers=get_auth_api_headers(bot=bot),
        allow_redirects=True,
    )
    status_code = response.status_code
    details = response.json()['details']
    if status_code in [200]:
        log.info(f"{response.json()}")
        tokens = response.json()['tokens']
        msg = []
        for token_dict in tokens:
            msg.append(f"Token ID - {token_dict['outline_id']}, срок действия - {token_dict['valid_until']}, "
                       f"демо ключ - {'Да' if token_dict['is_demo'] else 'Нет'}\n"
                       f"Ключ - {token_dict['vpn_key']}\n")
        bot.send_message(user_id, ''.join(msg) if msg else 'Ключи отсутствуют', reply_markup=main_keyboard())
    elif status_code in [404] and "User does not exist" in details:
        bot.send_message(
            user_id,
            "Вы не зарегистрированы.\nПожалуйста, пройдите регистрацию, нажав на соответствующую кнопку в Меню",
            reply_markup=main_keyboard()
        )
    else:
        send_alert_to_admins(bot, response, user)
        bot.send_message(user.id, f"{SERVER_EXCEPTION}\nВозврат в основное меню", reply_markup=main_keyboard())


def renew_token_step_1(message: Message, bot: TeleBot):
    bot.send_message(
        message.chat.id,
        'Введите ID ключа, который хотите перевыпустить.\n'
        'Если вы не знаете ID ключа, то в основном меню Вам необходимо'
        ' нажать на Мои VPN ключи, далее вернуться к перевыпуску ключа',
        reply_markup=back_to_main_menu_keyboard()
    )

    bot.register_next_step_handler(message, renew_token_step_2, bot)


def renew_token_step_2(message: Message, bot: TeleBot):
    if message.text in 'В основное меню':
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_keyboard())
    else:
        if not check_int(message.text):
            bot.send_message(message.chat.id, 'Вы ввели не число, повторите ввод',
                             reply_markup=back_to_main_menu_keyboard())
            bot.register_next_step_handler(message, renew_token_step_2, bot)
        else:
            user_id = message.from_user.id
            send_wait_message_to_user(bot, user_id)
            to_send = {
                'transport_name': BOT_NAME,
                'credentials': message.from_user.to_dict(),
                'outline_id': message.text
            }
            response = requests.post(
                f'{API_URL}{API_URIS["renew_exist_token"]}',
                headers=get_auth_api_headers(bot=bot),
                json=to_send,
                allow_redirects=True,
            )
            status_code = response.status_code
            details = response.json()['details']
            if status_code in [201]:
                token = response.json()['Tokens'][0]
                bot.send_message(
                    user_id,
                    f'Новый ключ создан.\n'
                    f'ID ключа - {token["outline_id"]}\n'
                    f'Срок действия, до- {token["valid_until"]}\n'
                    f'Ключ - {token["vpn_key"]}',
                    reply_markup=main_keyboard()
                )
            elif status_code in [403]:
                text = 'Что-то пошло не так. Свяжитесь с администратором или повторите попытку позже.'
                if 'Cannot' in details:
                    text = "Невозможно перевыпустить демо ключ. Проверьте корректность ID ключа и повторите ввод."
                elif 'belongs' in details:
                    text = "Ключ принадлежит другому пользователю, проверьте ID ключа и повторите ввод."
                bot.send_message(user_id, text, reply_markup=back_to_main_menu_keyboard())
                bot.register_next_step_handler(message, renew_token_step_2, bot)
            elif status_code in [404] and "User does not exist" in details:
                bot.send_message(
                    user_id,
                    "Вы не зарегистрированы.\nПожалуйста, пройдите регистрацию, нажав на соответствующую кнопку в Меню",
                    reply_markup=main_keyboard()
                )
            else:
                send_alert_to_admins(bot=bot, response=response, user=message.from_user)
                bot.send_message(user_id, f"{SERVER_EXCEPTION}\nВозврат в основное меню", reply_markup=main_keyboard())


def subscribes_step_1(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    send_wait_message_to_user(bot, user_id)
    available_tariffs_dicts = get_tariffs(bot=bot)
    available_tariffs_names = [tariff['name'] for tariff in available_tariffs_dicts]
    bot.send_message(
        user_id,
        'Выберите подписку',
        reply_markup=generate_action_keyboard(available_tariffs_names)
    )
    bot.register_next_step_handler(message, subscribes_step_2, bot, available_tariffs_dicts, available_tariffs_names)


def subscribes_step_2(message: Message, bot: TeleBot, available_tariffs_dicts: list, available_tariffs_names: list):
    user_id = message.from_user.id
    user_answer = message.text
    if user_answer in 'В основное меню':
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_keyboard())
    elif user_answer in available_tariffs_names:
        selected_tariff_dict = {}
        for tariff_dict in available_tariffs_dicts:
            if tariff_dict['name'] == user_answer:
                selected_tariff_dict = tariff_dict

        send_wait_message_to_user(bot, user_id)
        available_vpn_servers_dicts = get_vpn_servers(bot=bot)
        available_vpn_servers_names = [vpn_server['external_name'] for vpn_server in available_vpn_servers_dicts]
        bot.send_message(
            user_id,
            'Выберите сервер',
            reply_markup=generate_action_keyboard(available_vpn_servers_names),
        )
        bot.register_next_step_handler(
            message,
            subscribes_step_3,
            bot,
            selected_tariff_dict,
            available_vpn_servers_dicts,
            available_vpn_servers_names,
        )
    else:
        bot.send_message(user_id, 'Такой подписки не существует, повторите выбор')
        bot.register_next_step_handler(
            message,
            subscribes_step_2,
            bot,
            available_tariffs_dicts,
            available_tariffs_names,
        )


def subscribes_step_3(
        message: Message,
        bot: TeleBot,
        selected_tariff_dict: dict,
        available_vpn_servers_dicts: list,
        available_vpn_servers_names: list,
):
    user_answer = message.text
    user_id = message.chat.id
    if user_answer in 'В основное меню':
        bot.send_message(user_id, 'Возврат в основное меню', reply_markup=main_keyboard())
    elif user_answer in available_vpn_servers_names:
        selected_vpn_server_dict = {}
        for vpn_server_dict in available_vpn_servers_dicts:
            if vpn_server_dict['external_name'] == user_answer:
                selected_vpn_server_dict = vpn_server_dict
        if selected_tariff_dict['is_demo'] or selected_tariff_dict['is_tech']:
            send_wait_message_to_user(bot, user_id)
            to_send = {
                'transport_name': BOT_NAME,
                'credentials': message.from_user.to_dict(),
                'server_name': selected_vpn_server_dict['name'],
                'tariff': selected_tariff_dict,
            }
            response = requests.post(
                f'{API_URL}{API_URIS["create_new_token"]}',
                headers=get_auth_api_headers(bot=bot),
                json=to_send,
                allow_redirects=True,
            )
            status_code = response.status_code
            details = response.json()['details']
            if status_code == 201:
                token = response.json()['tokens'][0]
                bot.send_message(
                    user_id,
                    f'ID ключа - {token["outline_id"]}\nСрок действия до - {token["valid_until"]}'
                    f'\nЛимит траффика - {token["traffic_limit"] / 1024 / 1024} мб\nКлюч - {token["vpn_key"]}',
                    reply_markup=main_keyboard(),
                )
            elif status_code == 403:
                bot.send_message(
                    user_id,
                    "У Вас уже есть демо ключ.\nПолучение второго ключа не возможно\nВозврат в основное меню",
                    reply_markup=main_keyboard(),
                )
            elif status_code == 404 and "User does not exist" in details:
                bot.send_message(
                    user_id,
                    "Вы не зарегистрированы.\nПожалуйста, пройдите регистрацию, нажав на соответствующую кнопку в Меню",
                    reply_markup=main_keyboard()
                )
            else:
                send_alert_to_admins(bot=bot, response=response, user=message.from_user)
                bot.send_message(
                    user_id,
                    f"{SERVER_EXCEPTION}\nВозврат в основное меню",
                    reply_markup=main_keyboard()
                )
        else:
            send_wait_message_to_user(bot, user_id)
            send_msg_to_managers(
                bot=bot,
                message=message,
                text=f'Выбранный тариф:\n'
                     f'Наименование: {selected_tariff_dict["name"]}\n'
                     f'Срок действия: {selected_tariff_dict["prolong_period"]}\n'
                     f'Стоимость: {selected_tariff_dict["price"]}\n'
                     f'Выбранный сервер - {selected_vpn_server_dict}',
            )
            bot.send_message(
                user_id,
                'Выбранный сервер и тарифный план передан менеджеру.\nОжидайте ответ',
                reply_markup=main_keyboard(),
            )
    else:
        bot.send_message(user_id, 'Такого сервера не существует, повторите выбор')
        bot.register_next_step_handler(
            message,
            subscribes_step_3,
            bot,
            selected_tariff_dict,
            available_vpn_servers_dicts,
            available_vpn_servers_names
        )


def tariffs_step_1(bot: TeleBot, message: Message):
    user_id = message.chat.id
    send_wait_message_to_user(bot, user_id)
    tariffs = get_tariffs(bot=bot)
    msg = ['Доступные тарифы:\n']
    for tariff in tariffs:
        if tariff["traffic_limit"]:
            limit = f'Лимит трафика - {tariff["traffic_limit"] / 1024 / 1024} мб'
        else:
            limit = 'Без ограничения трафика'
        if tariff["price"]:
            price = f'стоимость - {tariff["price"]} {tariff["currency"]["name"]}'
        else:
            price = 'бесплатный'
        msg.append(f'Наименование: {tariff["name"]}, '
                   f'срок действия в днях: {tariff["prolong_period"]}\n'
                   f'{limit}, {price}\n'
                   )
    bot.send_message(user_id, '\n'.join(msg), reply_markup=main_keyboard())


def send_wait_message_to_user(bot: TeleBot, user_id: int):
    bot.send_message(user_id, 'Ваш запрос в очереди. Ожидайте.', reply_markup=types.ReplyKeyboardRemove())



# from telebot import TeleBot
# from telebot.types import Message
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
#
# # TODO: Ограничить количество демо ключей у пользователя
#
#
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

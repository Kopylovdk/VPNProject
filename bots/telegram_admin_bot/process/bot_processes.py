import requests
import logging
import os
from requests import Response
from telebot import TeleBot, types
from process.config_loader import CONFIG
from telebot.types import Message, User
from functools import lru_cache
from process.keyboards import (
    main_keyboard,
    generate_action_keyboard,
    back_to_main_menu_keyboard,
    token_actions_keyboard,
    yes_no_keyboard,
    back_keyboard,
    client_actions_keyboard,
    message_keyboard,
)

log = logging.getLogger(__name__)

API_CREDS_USERNAME = os.environ.get('USERNAME')
API_CREDS_PASSWORD = os.environ.get('PASSWORD')
API_URL = CONFIG['bot']['api']['url']
API_URL_HEALTH = CONFIG['bot']['api']['url_health']
API_URIS = CONFIG['bot']['api']['uris']
BOT_NAME = CONFIG['bot']['name']
TECH_ADMIN = CONFIG['bot']['admin_tech']


def check_int(data: str) -> int or str:
    try:
        int(data)
        return True
    except ValueError:
        return False


def health_check() -> Response:
    url = f'{API_URL_HEALTH}'
    response = requests.get(url, allow_redirects=True)
    return response


def send_alert_to_admins(bot: TeleBot, response: Response) -> None:
    """Функция отправки сообщений всем администратора"""
    text = f'ОШИБКА ПОДКЛЮЧЕНИЯ К БЭКУ:' \
           f' Status_code = {response.status_code!r},' \
           f' url = {response.url!r},' \
           f' headers = {response.headers}'
    log.error(f'{text!r}')

    for admin_id in TECH_ADMIN:
        bot.send_message(admin_id, text=text)


def send_wait_message_to_user(bot: TeleBot, user_id: int):
    bot.send_message(user_id, 'Ваш запрос в очереди. Ожидайте.', reply_markup=types.ReplyKeyboardRemove())


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
        return response.json()["tariffs"]
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


@lru_cache(maxsize=None)
def get_transports(bot: TeleBot) -> list:
    response = requests.get(
        f'{API_URL}{API_URIS["get_transports"]}',
        headers=get_auth_api_headers(bot=bot),
        allow_redirects=True,
    )
    if response.status_code == 200:
        log.info(f'get_transports executed')
        return response.json()["transports"]
    else:
        send_alert_to_admins(bot=bot, response=response)


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
            'Вы успешно зарегистрированы в боте для АДМИНИСТРАТОРОВ.',
            reply_markup=main_keyboard(),
        )
        log.info(f'{json_response["details"]}:\n{json_response["user_info"]}')
    else:
        send_alert_to_admins(bot, response)
        log.error(f'add or update error {response}, {message}')


def transfer_token_data_ids_to_names(bot: TeleBot, token_dict: dict) -> dict:
    tariffs = get_tariffs(bot=bot)
    servers = get_vpn_servers(bot=bot)
    for token_key, token_item in token_dict.items():
        if token_key == 'server':
            for server in servers:
                if server['id'] == token_item:
                    token_dict['server'] = server['name']
                    break
        if token_key == 'tariff':
            for tariff in tariffs:
                if tariff['id'] == token_item:
                    token_dict['tariff'] = tariff['name']
                    break
    return token_dict


def select_action_with_token_step_1(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    bot.send_message(user_id, 'Введите ID VPN ключа для дальнейшей работы.', reply_markup=back_to_main_menu_keyboard())
    bot.register_next_step_handler(message, select_action_with_token_step_2, bot)


def select_action_with_token_step_2(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    user_answer = message.text
    if 'В основное меню' in user_answer:
        bot.send_message(user_id, 'Возврат в основное меню', reply_markup=main_keyboard())
    else:
        if check_int(user_answer):
            send_wait_message_to_user(bot=bot, user_id=user_id)
            token_id = user_answer
            response = requests.get(
                f'{API_URL}{API_URIS["get_token_info"].format(token_id=token_id)}',
                headers=get_auth_api_headers(bot=bot),
                allow_redirects=True,
            )
            status_code = response.status_code
            if status_code == 200:
                token_dict = response.json()['tokens'][0]
                token_dict = transfer_token_data_ids_to_names(bot, token_dict)
                bot.send_message(
                    user_id,
                    'Выберите действие',
                    reply_markup=token_actions_keyboard(token_dict)
                )
                bot.register_next_step_handler(message, select_action_with_token_step_3, bot, token_dict)

            elif status_code == 404:
                bot.send_message(
                    user_id,
                    f'Повторите ввод, такого ключа не существует. err={response.json()["details"]!r}',
                    reply_markup=back_to_main_menu_keyboard()
                )
                bot.register_next_step_handler(message, select_action_with_token_step_2, bot)

        else:
            bot.send_message(user_id, 'Вы ввели не число, повторите ввод', reply_markup=back_to_main_menu_keyboard())
            bot.register_next_step_handler(message, select_action_with_token_step_2, bot)


def select_action_with_token_step_3(message: Message, bot: TeleBot, token_dict: dict):
    user_id = message.from_user.id
    user_answer = message.text
    if 'В основное меню' in user_answer:
        bot.send_message(user_id, 'Возврат в основное меню', reply_markup=main_keyboard())
    elif 'Информация о ключе' in user_answer:
        traffic_limit = "Отсутствует"
        if token_dict["traffic_limit"]:
            traffic_limit = token_dict["traffic_limit"] / 1024 / 1024
        valid_until = "Отсутствует"
        if token_dict["valid_until"]:
            valid_until = token_dict["valid_until"]
        bot.send_message(
            user_id,
            f'Данные по выбранному ключу:\n'
            f'ID: {token_dict["id"]}\n'
            f'Имя ключа: {token_dict["name"]}\n'
            f'Server: {token_dict["server"]}\n'
            f'Тариф: {token_dict["tariff"]}\n'
            f'Outline_id: {token_dict["outline_id"]}\n'
            f'ID предыдущей записи: {token_dict["previous_vpn_token_id"]}\n'
            f'Срок действия: {valid_until}\n'
            f'Лимит трафика, мб: {traffic_limit}\n'
            f'Активность: {"Активен" if token_dict["is_active"] else "Неактивен"}\n'
            f'Демо ключ: {"Да" if token_dict["is_demo"] else "Нет"}\n'
            f'Ключ доступа = {token_dict["vpn_key"]}\n',
            reply_markup=token_actions_keyboard(token_dict)
        )
        bot.register_next_step_handler(message, select_action_with_token_step_3, bot, token_dict)

    elif 'Перевыпустить VPN ключ' in user_answer:
        bot.send_message(user_id, 'Вы действительно перевыпустить выбранный ключ?', reply_markup=yes_no_keyboard())
        bot.register_next_step_handler(message, token_renew_step_1, bot, token_dict)

    elif 'Изменить срок действия' in user_answer:
        bot.send_message(
            user_id,
            'Введите НОВЫЙ срок действия в днях.\n При вводе 0 срок действия будет убран'
            'ВНИМАНИЕ!! Новый срок действия будет с сегодняшнего дня, а не прибавлен к текущему',
            reply_markup=back_keyboard()
        )
        bot.register_next_step_handler(message, token_valid_until_update_step_1, bot, token_dict)

    elif 'Установить лимит трафика' in user_answer:
        bot.send_message(user_id, 'Введите лимит трафика в мегабайтах.', reply_markup=back_keyboard())
        bot.register_next_step_handler(message, token_traffic_limit_update_step_1, bot, token_dict)
    elif 'Снять лимит трафика' in user_answer:
        token_traffic_limit_delete(bot, token_dict, message)
    elif 'Удалить ключ' in user_answer:
        bot.send_message(user_id, 'Вы действительно хотите удалить ключ?', reply_markup=yes_no_keyboard())
        bot.register_next_step_handler(message, token_delete_step_1, bot, token_dict)
    elif 'Выбрать другой VPN ключ' in user_answer:
        select_action_with_token_step_1(message, bot)
    else:
        bot.send_message(
            user_id,
            'Такой команды не существует, повторите выбор',
            reply_markup=token_actions_keyboard(token_dict)
        )
        bot.register_next_step_handler(message, select_action_with_token_step_3, bot, token_dict)


def select_action_response_handler(response: Response, bot: TeleBot, token_dict: dict, message: Message):
    user_id = message.from_user.id
    status_code = response.status_code
    if status_code in [200, 201]:
        data = response.json()
        new_token_dict = data['tokens'][0]
        new_token_dict['server'] = token_dict['server']
        new_token_dict['tariff'] = token_dict['tariff']
        bot.send_message(user_id, data['details'], reply_markup=token_actions_keyboard(new_token_dict))
        bot.register_next_step_handler(message, select_action_with_token_step_3, bot, new_token_dict)
    elif status_code != 500:
        bot.send_message(
            user_id,
            f'Ошибка {response!r}, {response.json()!r}, {response.json()["details"]!r}',
            reply_markup=token_actions_keyboard(token_dict)
        )
        bot.register_next_step_handler(message, select_action_with_token_step_3, bot, token_dict)
    else:
        bot.send_message(
            user_id,
            f'Ошибка {response!r}, возврат в основное меню',
            reply_markup=main_keyboard()
        )


def token_renew_step_1(message: Message, bot: TeleBot, token_dict: dict):
    user_id = message.from_user.id
    user_answer = message.text
    if user_answer in ['Нет']:
        bot.send_message(user_id, 'Возврат в предыдущее меню', reply_markup=token_actions_keyboard(token_dict))
        bot.register_next_step_handler(message, select_action_with_token_step_3, bot, token_dict)
    elif 'Да' in user_answer:
        send_wait_message_to_user(bot=bot, user_id=user_id)
        to_send = {
            'token_id': token_dict['id'],
        }
        response = requests.post(
            f'{API_URL}{API_URIS["renew_exist_token"]}',
            headers=get_auth_api_headers(bot=bot),
            json=to_send,
            allow_redirects=True,
        )
        select_action_response_handler(response, bot, token_dict, message)
    else:
        bot.send_message(user_id, 'Такой команды не существует, повторите выбор', reply_markup=yes_no_keyboard())
        bot.register_next_step_handler(message, token_renew_step_1, bot, token_dict)


def token_traffic_limit_delete(bot: TeleBot, token_dict: dict, message: Message):
    send_wait_message_to_user(bot=bot, user_id=message.from_user.id)
    to_send = {"token_id": token_dict['id']}
    response = requests.patch(
        f'{API_URL}{API_URIS["update_token"]}',
        headers=get_auth_api_headers(bot=bot),
        json=to_send,
        allow_redirects=True,
    )
    select_action_response_handler(response, bot, token_dict, message)


def token_traffic_limit_update_step_1(message: Message, bot: TeleBot, token_dict: dict):
    user_id = message.from_user.id
    user_answer = message.text
    if user_answer in ['Назад']:
        bot.send_message(user_id, 'Возврат в предыдущее меню', reply_markup=token_actions_keyboard(token_dict))
        bot.register_next_step_handler(message, select_action_with_token_step_3, bot, token_dict)
    else:
        if check_int(user_answer):
            send_wait_message_to_user(bot=bot, user_id=user_id)
            to_send = {
                "token_id": token_dict['id'],
                "traffic_limit": str(user_answer),
            }
            response = requests.patch(
                f'{API_URL}{API_URIS["update_token"]}',
                headers=get_auth_api_headers(bot=bot),
                json=to_send,
                allow_redirects=True,
            )
            select_action_response_handler(response, bot, token_dict, message)
        else:
            bot.send_message(user_id, 'Вы ввели не целое число, повторите ввод', reply_markup=back_keyboard())
            bot.register_next_step_handler(message, token_traffic_limit_update_step_1, bot, token_dict)


def token_valid_until_update_step_1(message: Message, bot: TeleBot, token_dict: dict):
    user_id = message.from_user.id
    user_answer = message.text
    if user_answer in ['Назад']:
        bot.send_message(user_id, 'Возврат в предыдущее меню', reply_markup=token_actions_keyboard(token_dict))
        bot.register_next_step_handler(message, select_action_with_token_step_3, bot, token_dict)
    else:
        if check_int(user_answer):
            send_wait_message_to_user(bot=bot, user_id=user_id)
            to_send = {
                "token_id": token_dict['id'],
                "valid_until": str(user_answer),
            }
            response = requests.patch(
                f'{API_URL}{API_URIS["update_token"]}',
                headers=get_auth_api_headers(bot=bot),
                json=to_send,
                allow_redirects=True,
            )
            select_action_response_handler(response, bot, token_dict, message)
        else:
            bot.send_message(user_id, 'Вы ввели не целое число, повторите ввод', reply_markup=back_keyboard())
            bot.register_next_step_handler(message, token_valid_until_update_step_1, bot, token_dict)


def token_delete_step_1(message: Message, bot: TeleBot, token_dict: dict):
    user_id = message.from_user.id
    user_answer = message.text
    if user_answer in ['Нет']:
        bot.send_message(user_id, 'Возврат в предыдущее меню', reply_markup=token_actions_keyboard(token_dict))
        bot.register_next_step_handler(message, select_action_with_token_step_3, bot, token_dict)
    elif 'Да' in user_answer:
        send_wait_message_to_user(bot=bot, user_id=user_id)
        to_send = {'token_id': token_dict['id']}
        response = requests.delete(
            f'{API_URL}{API_URIS["delete_token"]}',
            headers=get_auth_api_headers(bot=bot),
            json=to_send,
            allow_redirects=True,
        )
        select_action_response_handler(response, bot, token_dict, message)
    else:
        bot.send_message(user_id, 'Такой команды не существует, повторите выбор', reply_markup=yes_no_keyboard())
        bot.register_next_step_handler(message, token_delete_step_1, bot, token_dict)


def select_action_with_user_step_1(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    send_wait_message_to_user(bot=bot, user_id=user_id)
    transports = get_transports(bot=bot)
    list_for_kb = []
    for item in transports:
        list_for_kb.append(item['name'])

    bot.send_message(
        user_id,
        'Выберите Бота по которому клиент пришел.',
        reply_markup=generate_action_keyboard(list_for_kb),
    )
    bot.register_next_step_handler(message, select_action_with_user_step_2, bot, list_for_kb)


def select_action_with_user_step_2(message: Message, bot: TeleBot, list_for_kb: list):
    user_id = message.from_user.id
    user_answer = message.text
    if 'В основное меню' in user_answer:
        bot.send_message(user_id, 'Возврат в основное меню', reply_markup=main_keyboard())
    elif user_answer in list_for_kb:
        to_send = {
            'transport_name': user_answer,
            'messenger_id': int,
        }
        bot.send_message(user_id, 'Введите ID пользователя telegram', reply_markup=back_to_main_menu_keyboard())
        bot.register_next_step_handler(message, select_action_with_user_step_3, bot, to_send)

    else:
        bot.send_message(
            user_id,
            'Такого Бота не существует, повторите выбор',
            reply_markup=generate_action_keyboard(list_for_kb),
        )
        bot.register_next_step_handler(message, select_action_with_user_step_2, bot, list_for_kb)


def select_action_with_user_step_3(message: Message, bot: TeleBot, to_send: dict):
    user_id = message.from_user.id
    user_answer = message.text
    if 'В основное меню' in user_answer:
        bot.send_message(user_id, 'Возврат в основное меню', reply_markup=main_keyboard())
    elif check_int(user_answer):
        send_wait_message_to_user(bot=bot, user_id=user_id)

        to_send['messenger_id'] = user_answer
        response = requests.get(
            f'{API_URL}{API_URIS["get_contact"].format(**to_send)}',
            headers=get_auth_api_headers(bot=bot),
            allow_redirects=True,
        )
        status_code = response.status_code
        if status_code == 200:
            user_info = response.json()['user_info']
            bot.send_message(
                user_id,
                f'Данные по выбранному ключу:\n'
                f'Клиент: {user_info["user"]["full_name"]}\n'
                f'Бот для связи: {to_send["transport_name"]}\n'
                f'TG ID: {user_info["contact"]["credentials"]["id"]}\n'
                f'uid: {user_info["contact"]["uid"]}\n'
                f'Телефон: {user_info["contact"]["phone_number"]}\n',
                reply_markup=client_actions_keyboard()
            )
            bot.register_next_step_handler(message, select_action_with_user_step_4, bot, to_send, user_info)
        elif status_code != 500:
            bot.send_message(
                user_id,
                f'Ошибка {response!r}, {response.json()!r}, {response.json()["details"]!r}',
                reply_markup=main_keyboard()
            )
        else:
            bot.send_message(
                user_id,
                f'Ошибка {response!r}, возврат в основное меню',
                reply_markup=main_keyboard()
            )
    else:
        bot.send_message(user_id, 'Вы ввели не целое число, повторите ввод', reply_markup=back_to_main_menu_keyboard())
        bot.register_next_step_handler(message, select_action_with_user_step_3, bot, to_send)


def select_action_with_user_step_4(message: Message, bot: TeleBot, to_send: dict, user_info: dict):
    user_id = message.from_user.id
    user_answer = message.text
    if 'В основное меню' in user_answer:
        bot.send_message(user_id, 'Возврат в основное меню', reply_markup=main_keyboard())
    elif 'Выбранный пользователь' in user_answer:
        bot.send_message(
            user_id,
            f'Данные по выбранному ключу:\n'
            f'Клиент: {user_info["user"]["full_name"]}\n'
            f'Бот для связи: {to_send["transport_name"]}\n'
            f'TG ID: {user_info["contact"]["credentials"]["id"]}\n'
            f'uid: {user_info["contact"]["uid"]}\n'
            f'Телефон: {user_info["contact"]["phone_number"]}\n',
            reply_markup=client_actions_keyboard(),
        )
        bot.register_next_step_handler(message, select_action_with_user_step_4, bot, to_send, user_info)
    elif 'Список ВСЕХ ключей пользователя' in user_answer:
        get_vpn_keys_step_1(message, bot, to_send, user_info)
    elif 'Сменить пользователя и/или бота' in user_answer:
        select_action_with_user_step_1(message, bot)
    else:
        bot.send_message(
            user_id,
            'Такой команды не существует, повторите выбор',
            reply_markup=client_actions_keyboard()
        )
        bot.register_next_step_handler(message, select_action_with_user_step_4, bot, to_send, user_info)


def get_vpn_keys_step_1(message: Message, bot: TeleBot, to_send: dict, user_info: dict):
    user_id = message.from_user.id
    send_wait_message_to_user(bot=bot, user_id=user_id)
    response = requests.get(
        f'{API_URL}{API_URIS["get_client_tokens"].format(**to_send)}',
        headers=get_auth_api_headers(bot=bot),
        allow_redirects=True,
    )
    status_code = response.status_code
    if status_code == 200:
        tokens = response.json()['tokens']
        msg = []
        for token_dict in tokens:
            msg.append(f"Token ID - {token_dict['id']}, срок действия - {token_dict['valid_until']}, "
                       f"демо ключ - {'Да' if token_dict['is_demo'] else 'Нет'}\n"
                       f"Ключ - {token_dict['vpn_key']}\n")
        bot.send_message(user_id, ''.join(msg) if msg else 'Ключи отсутствуют', reply_markup=client_actions_keyboard())
        bot.register_next_step_handler(message, select_action_with_user_step_4, bot, to_send, user_info)
    elif status_code != 500:
        bot.send_message(
            user_id,
            f'Ошибка {response!r}, {response.json()!r}, {response.json()["details"]!r}',
            reply_markup=client_actions_keyboard(),
        )
        bot.register_next_step_handler(message, select_action_with_user_step_4, bot,  to_send, user_info)
    else:
        bot.send_message(
            user_id,
            f'Ошибка {response!r}, возврат в основное меню',
            reply_markup=main_keyboard()
        )


def new_token_step_1(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    send_wait_message_to_user(bot=bot, user_id=user_id)
    servers = get_vpn_servers(bot=bot)
    list_for_kb = []
    for server in servers:
        list_for_kb.append(server['external_name'])
    bot.send_message(user_id, 'Выберите сервер', reply_markup=generate_action_keyboard(list_for_kb))
    bot.register_next_step_handler(message, new_token_step_2, bot, servers, list_for_kb)


def new_token_step_2(message: Message, bot: TeleBot, servers: list[dict], list_for_kb: list):
    user_id = message.from_user.id
    user_answer = message.text
    if 'В основное меню' in user_answer:
        bot.send_message(user_id, 'Возврат в основное меню', reply_markup=main_keyboard())
    elif user_answer in list_for_kb:
        send_wait_message_to_user(bot=bot, user_id=user_id)
        to_send = {
            'server_name': str,
            'tariff_name': str,
        }
        for server in servers:
            if server['external_name'] == user_answer:
                to_send['server_name'] = server['name']
        tariffs = get_tariffs(bot=bot)
        list_for_kb = []
        for tariff in tariffs:
            list_for_kb.append(tariff['name'])
        bot.send_message(message.from_user.id, 'Выберите тариф', reply_markup=generate_action_keyboard(list_for_kb))
        bot.register_next_step_handler(message, new_token_step_3, bot, list_for_kb, to_send)
    else:
        bot.send_message(
            user_id,
            'Такого сервера не существует, повторите выбор',
            reply_markup=generate_action_keyboard(list_for_kb),
        )
        bot.register_next_step_handler(message, new_token_step_2, bot, list_for_kb)


def new_token_step_3(message: Message, bot: TeleBot, list_for_kb: list, to_send: dict):
    user_id = message.from_user.id
    user_answer = message.text
    if 'В основное меню' in user_answer:
        bot.send_message(user_id, 'Возврат в основное меню', reply_markup=main_keyboard())
    elif user_answer in list_for_kb:
        send_wait_message_to_user(bot=bot, user_id=user_id)
        to_send['tariff_name'] = user_answer
        response = requests.post(
            f'{API_URL}{API_URIS["create_new_token"]}',
            headers=get_auth_api_headers(bot=bot),
            json=to_send,
            allow_redirects=True,
        )
        status_code = response.status_code
        if status_code in [201]:
            data = response.json()
            text = f'Владелец:\n' \
                   f'id: {data["user_info"]["user"]["id"]}\n' \
                   f'ФИО: {data["user_info"]["user"]["full_name"]}\n' \
                   f'Новый ключ:\n' \
                   f'id: {data["tokens"][0]["id"]}\n' \
                   f'Срок действия: {data["tokens"][0]["valid_until"]}\n' \
                   f'Ключ: {data["tokens"][0]["vpn_key"]}'
            bot.send_message(user_id, text, reply_markup=main_keyboard())

        elif status_code != 500:
            bot.send_message(
                user_id,
                f'Ошибка {response!r}, {response.json()!r}, {response.json()["details"]!r}',
                reply_markup=main_keyboard(),
            )
        else:
            bot.send_message(
                user_id,
                f'Ошибка {response!r}, возврат в основное меню',
                reply_markup=main_keyboard()
            )
    else:
        bot.send_message(
            user_id,
            'Такого тарифа не существует, повторите выбор',
            reply_markup=generate_action_keyboard(list_for_kb),
        )
        bot.register_next_step_handler(message, new_token_step_3, bot, list_for_kb, to_send)


def select_message_send_type_step_1(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    send_wait_message_to_user(bot=bot, user_id=user_id)
    transports = get_transports(bot=bot)
    list_for_kb = []
    for item in transports:
        list_for_kb.append(item['name'])

    bot.send_message(
        user_id,
        'Выберите Бота от которого будет необходимо отправить сообщение',
        reply_markup=generate_action_keyboard(list_for_kb),
    )
    bot.register_next_step_handler(message, select_message_send_type_step_2, bot, list_for_kb)


def select_message_send_type_step_2(message: Message, bot: TeleBot, list_for_kb: list):
    user_id = message.from_user.id
    user_answer = message.text
    if 'В основное меню' in user_answer:
        bot.send_message(user_id, 'Возврат в основное меню', reply_markup=main_keyboard())
    elif user_answer in list_for_kb:
        to_send = {
            'transport_name': user_answer,
            'text': str,
            'messenger_id': None,
        }
        bot.send_message(user_id, 'Введите текст сообщения', reply_markup=back_to_main_menu_keyboard())
        bot.register_next_step_handler(message, select_message_send_type_step_3, bot, to_send)

    else:
        bot.send_message(
            user_id,
            'Такого Бота не существует, повторите выбор',
            reply_markup=generate_action_keyboard(list_for_kb),
        )
        bot.register_next_step_handler(message, select_message_send_type_step_2, bot, list_for_kb)


def select_message_send_type_step_3(message: Message, bot: TeleBot, to_send: dict):
    user_id = message.from_user.id
    user_answer = message.text
    if 'В основное меню' in user_answer:
        bot.send_message(user_id, 'Возврат в основное меню', reply_markup=main_keyboard())
    else:
        to_send['text'] = user_answer
        bot.send_message(
            user_id,
            f'Проверьте сообщение, если все хорошо нажмите Да, иначе Нет.\n{to_send["text"]}',
            reply_markup=yes_no_keyboard()
        )
        bot.register_next_step_handler(message, select_message_send_type_step_4, bot, to_send)


def select_message_send_type_step_4(message: Message, bot: TeleBot, to_send: dict):
    user_id = message.from_user.id
    user_answer = message.text
    if 'Нет' in user_answer:
        bot.send_message(user_id, 'Повторите ввод', reply_markup=back_to_main_menu_keyboard())
        bot.register_next_step_handler(message, select_message_send_type_step_3, to_send)
    elif 'Да' in user_answer:
        bot.send_message(message.chat.id, 'Выберите вариант отправки сообщения', reply_markup=message_keyboard())
        bot.register_next_step_handler(message, select_message_send_type_step_5, bot, to_send)
    else:
        bot.send_message(
            user_id,
            'Такой команды не существует, повторите выбор',
            reply_markup=yes_no_keyboard()
        )
        bot.register_next_step_handler(message, select_message_send_type_step_4, bot, to_send)


def message_response_handler(response: Response, bot: TeleBot, message: Message):
    user_id = message.from_user.id
    status_code = response.status_code
    if status_code == 200:
        data = response.json()
        bot.send_message(
            user_id,
            f'{data["details"]}\n'
            f'Статистика:\n'
            f'Успешно отправлено: {data["info"]["success"]}\n'
            f'Ошибка отправки: {data["info"]["error"]}',
            reply_markup=main_keyboard(),
        )
    elif status_code != 500:
        bot.send_message(
            user_id,
            f'Ошибка {response!r}, {response.json()!r}, {response.json()["details"]!r} возврат в основное меню',
            reply_markup=main_keyboard(),
        )
    else:
        bot.send_message(
            user_id,
            f'Ошибка {response!r}, возврат в основное меню',
            reply_markup=main_keyboard()
        )


def select_message_send_type_step_5(message: Message, bot: TeleBot, to_send: dict):
    user_id = message.from_user.id
    user_answer = message.text
    if 'В основное меню' in user_answer:
        bot.send_message(user_id, 'Возврат в основное меню', reply_markup=main_keyboard())
    elif 'Всем' in user_answer:
        send_wait_message_to_user(bot=bot, user_id=user_id)
        response = requests.post(
            f'{API_URL}{API_URIS["telegram_message_send"]}',
            headers=get_auth_api_headers(bot=bot),
            json=to_send,
            allow_redirects=True,
        )
        message_response_handler(response, bot, message)

    elif 'Лично' in user_answer:
        bot.send_message(user_id, 'Введите ID пользователя telegram', reply_markup=back_to_main_menu_keyboard())
        bot.register_next_step_handler(message, select_message_send_type_step_6, bot, to_send)

    else:
        bot.send_message(
            user_id,
            'Такой команды не существует, повторите выбор',
            reply_markup=message_keyboard(),
        )
        bot.register_next_step_handler(message, select_message_send_type_step_5, bot, to_send)


def select_message_send_type_step_6(message: Message, bot: TeleBot, to_send: dict):
    user_id = message.from_user.id
    user_answer = message.text
    if 'В основное меню' in user_answer:
        bot.send_message(user_id, 'Возврат в основное меню', reply_markup=main_keyboard())
    elif check_int(user_answer):
        send_wait_message_to_user(bot=bot, user_id=user_id)
        to_send['messenger_id'] = user_answer
        response = requests.post(
            f'{API_URL}{API_URIS["telegram_message_send"]}',
            headers=get_auth_api_headers(bot=bot),
            json=to_send,
            allow_redirects=True,
        )
        message_response_handler(response, bot, message)
    else:
        bot.send_message(user_id, 'Вы ввели не целое число, повторите ввод', reply_markup=back_to_main_menu_keyboard())
        bot.register_next_step_handler(message, select_message_send_type_step_6, bot, to_send)

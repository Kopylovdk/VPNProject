import datetime
import re
import requests
import logging
import os
from requests import Response
from telebot import TeleBot, types
from telebot.apihelper import ApiTelegramException
from exceptions.bot_exceptions import SERVER_EXCEPTION
from configs.config_loader import CONFIG
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
API_URL_HEALTH = CONFIG['bot']['api']['url_health']
API_URIS = CONFIG['bot']['api']['uris']
BOT_NAME = CONFIG['bot']['name']
ADMIN_ALERT = CONFIG['bot']['admin_alert']
MANAGERS = CONFIG['bot']['managers']
_cache_update_date = None


def format_bytes_to_human(size: int) -> str:
    info_size = 1024
    n = 0
    info_labels = ['байт', 'Кб', 'Мб', 'Гб', 'Тб', 'Пб', 'Эб', 'Зб', 'Йб']
    while size >= info_size:
        size /= info_size
        n += 1
    return f"{size:.2f} {info_labels[n]}"


def get_actual_cache_date(bot: TeleBot) -> datetime.datetime:
    response = requests.get(
        f'{API_URL}{API_URIS["get_actual_cache_date"]}',
        headers=get_auth_api_headers(bot=bot),
        allow_redirects=True,
    )
    if response.status_code == 200:
        log.debug(f'get_actual_cache_date {datetime.datetime.fromisoformat(response.json()["cache_update_date"])}')
        return datetime.datetime.fromisoformat(response.json()["cache_update_date"])
    else:
        send_alert_to_admins(bot=bot, response=response)


def check_cache_date(bot: TeleBot) -> None:
    global _cache_update_date
    new_date = get_actual_cache_date(bot=bot)
    if _cache_update_date:
        if _cache_update_date < new_date:
            _cache_update_date = new_date
            clear_cache()
    else:
        _cache_update_date = new_date


def clear_cache():
    get_vpn_servers.cache_clear()
    get_tariffs.cache_clear()


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
def get_tariffs(bot: TeleBot) -> Response:
    log.info(f'get_tariffs executed.')
    return requests.get(
        f'{API_URL}{API_URIS["get_tariffs"]}',
        headers=get_auth_api_headers(bot=bot),
        allow_redirects=True,
    )


def subscribe_channel(bot: TeleBot, message: Message) -> None:
    bot.send_message(
        message.chat.id,
        "Подписаться на группу [Tematika VPN Official](https://t.me/tematikavpn)",
        reply_markup=main_keyboard(),
        parse_mode='MarkdownV2',
    )


def update_tariffs(bot) -> list:
    check_cache_date(bot=bot)
    response = get_tariffs(bot=bot)
    if response.status_code == 200:
        json_data = response.json()
        tariffs = json_data["tariffs"]
        for i, tariff in enumerate(tariffs):
            if tariff['is_tech']:
                del tariffs[i]
        return tariffs
    else:
        send_alert_to_admins(bot=bot, response=response)


@lru_cache(maxsize=None)
def get_vpn_servers(bot: TeleBot) -> Response:
    log.info('get_vpn_servers executed')
    return requests.get(
        f'{API_URL}{API_URIS["get_vpn_servers"]}',
        headers=get_auth_api_headers(bot=bot),
        allow_redirects=True,
    )


def update_vpn_servers(bot: TeleBot) -> list:
    check_cache_date(bot=bot)
    response = get_vpn_servers(bot=bot)
    if response.status_code == 200:
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
    json_data = response.json()
    if status_code == 200:
        return json_data
    elif status_code in [404] and "User does not exist" in json_data['details']:
        bot.send_message(
            messenger_id,
            "Вы не зарегистрированы.\nПожалуйста, пройдите регистрацию, нажав на соответствующую кнопку в Меню",
            reply_markup=main_keyboard()
        )
        return {'details': 'No register'}
    else:
        send_alert_to_admins(bot=bot, response=response)


def send_alert_to_admins(bot: TeleBot, response: Response, user: User = None) -> None:
    """Функция отправки сообщений всем администратора"""
    err = f'Ошибка {response!r}, возврат в основное меню'
    try:
        json_data = response.json()
        err = f'Ошибка {response!r}, {json_data!r}, {json_data!r} возврат в основное меню'
    except requests.exceptions.JSONDecodeError:
        pass

    if user:
        text = f'ОШИБКА У КЛИЕНТА:\n' \
               f'Пользователь:\n' \
               f'ID - {user.id!r}\n' \
               f'Логин - {user.username!r}\n' \
               f'ФИО - {user.full_name!r}\n' \
               f'Произошла ошибка:\n' \
               f'Response = {err}'
        log.error(f'{err!r}, {text!r}')
    else:
        text = f'ОШИБКА ПОДКЛЮЧЕНИЯ К БЭКУ:' \
               f' Response = {err!r},' \
               f' url = {response.url!r},' \
               f' headers = {response.headers}'
        log.error(f'{text!r}')

    for admin_id in ADMIN_ALERT:
        bot.send_message(admin_id, text=text)


def send_msg_to_managers(bot: TeleBot, text: str, message: Message) -> None:
    """Функция отправки сообщений всем менеджерам"""
    response = get_client(bot, message.from_user.id)
    if "No register" in response['details']:
        text_2 = 'для не зарегистрированного пользователя'
    else:
        text_2 = f'Номер телефона - {response["user_info"]["contact"]["phone_number"]!r}'
    for manager_id in MANAGERS:
        try:
            bot.send_message(
                manager_id,
                text=f'Пользователь:\n'
                     f'ID - {message.from_user.id!r}\n'
                     f'Логин - {message.from_user.username!r}\n'
                     f'ФИО - {message.from_user.full_name!r}\n'
                     f"{text_2}\n"
                     f'{text}',
            )
            bot.forward_message(
                chat_id=manager_id,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
            )
        except ApiTelegramException:
            continue


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
        json_data = response.json()
        bot.send_message(
            message.chat.id,
            'Вы успешно зарегистрированы. Теперь Вам доступен весь функционал.',
            reply_markup=main_keyboard(),
        )
        log.info(f'{json_data["details"]}:\n{json_data["user_info"]}')
    else:
        bot.send_message(message.chat.id, SERVER_EXCEPTION, reply_markup=main_keyboard())
        send_alert_to_admins(bot, response, message.from_user)
        log.error(f'add or update error {response}, {message}')


def text_replace_for_markdown(text: str) -> str:
    replacements = {
        '-': '\-',
        '_': '\_',
        '.': '\.',
        ',': '\,',
        '<': '\<',
        '>': '\>',
        '[': '\[',
        ']': '\]',
        '(': '\(',
        ')': '\)',
    }
    rep_sorted = sorted(replacements, key=len, reverse=True)
    rep_escaped = map(re.escape, rep_sorted)
    pattern = re.compile("|".join(rep_escaped), 0)
    return pattern.sub(lambda match: replacements[match.group(0)], text)


def transfer_token_data_ids_to_names(bot: TeleBot, token_dict: dict) -> dict:
    tariffs = update_tariffs(bot=bot)
    servers = update_vpn_servers(bot=bot)
    for token_key, token_item in token_dict.items():
        if token_key == 'server':
            for server in servers:
                if server['id'] == token_item:
                    token_dict['server'] = server['external_name']
                    break
        if token_key == 'tariff':
            for tariff in tariffs:
                if tariff['id'] == token_item:
                    token_dict['tariff'] = tariff['name']
                    break
    return token_dict


def prepare_token_to_send(token_dict: dict, bot: TeleBot) -> str:
    token_dict = transfer_token_data_ids_to_names(bot=bot, token_dict=token_dict)
    if token_dict['valid_until']:
        valid_until = f'срок действия до: *{token_dict["valid_until"]}*'
    else:
        valid_until = '*без ограничения* по сроку'
    if token_dict['traffic_limit']:
        rest_of_traffic = token_dict["traffic_limit"] - (token_dict["traffic_used"] if token_dict["traffic_used"] else 0)
        traffic_limit = f'лимит трафика: *{format_bytes_to_human(token_dict["traffic_limit"])}*,' \
                        f' остаток {format_bytes_to_human(rest_of_traffic)}'
    else:
        traffic_limit = '*без ограничения* трафика'
    return f"Token ID: *{token_dict['id']}*, {valid_until}, "\
           f"демо ключ - *{'Да' if token_dict['is_demo'] else 'Нет'}*, "\
           f"{traffic_limit}, сервер: *{token_dict['server']}*"\
           f"\nКлюч: `{token_dict['vpn_key']}`\n "


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
    json_data = response.json()
    if status_code in [200]:
        log.info(f"{response.json()}")
        tokens = json_data['tokens']
        msg = []
        for token_dict in tokens:
            msg.append(
                text_replace_for_markdown(
                    prepare_token_to_send(token_dict, bot)
                )
            )
        bot.send_message(user_id, 'Для копирования ключа тапните на него.', reply_markup=main_keyboard())
        bot.send_message(
            user_id, ''.join(msg) if msg else 'Ключи отсутствуют',
            reply_markup=main_keyboard(),
            parse_mode='MarkdownV2',
        )
    elif status_code in [404] and "User does not exist" in json_data['details']:
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
                'token_id': message.text,
            }
            response = requests.post(
                f'{API_URL}{API_URIS["renew_exist_token"]}',
                headers=get_auth_api_headers(bot=bot),
                json=to_send,
                allow_redirects=True,
            )
            json_data = response.json()
            status_code = response.status_code
            details = json_data['details']
            if status_code in [201]:
                token = json_data['tokens'][0]
                renew_text = f'Новый ключ создан.\n Старый ключ более не действителен, замените его в приложении.\n' \
                             f'Для копирования ключа тапните на него.\n'
                text = text_replace_for_markdown(prepare_token_to_send(token, bot))
                bot.send_message(user_id, renew_text, reply_markup=main_keyboard())
                bot.send_message(user_id, text, reply_markup=main_keyboard(), parse_mode='MarkdownV2')
            elif status_code in [403]:
                text = 'Что-то пошло не так. Свяжитесь с администратором или повторите попытку позже.'
                if 'Cannot' in details:
                    text = "Невозможно перевыпустить демо ключ. Проверьте корректность ID ключа."
                elif 'belongs' in details:
                    text = "Ключ принадлежит другому пользователю. Проверьте корректность ID ключа."
                elif 'not active' in details:
                    text = "Не возможно перевыпустить неактивный ключ. Проверьте список своих ключей"
                bot.send_message(user_id, text, reply_markup=main_keyboard())
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
    available_tariffs_dicts = update_tariffs(bot=bot)
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
        available_vpn_servers_dicts = update_vpn_servers(bot=bot)
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
        available_vpn_servers_dicts: dict,
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
                'tariff_name': selected_tariff_dict['name'],
            }
            response = requests.post(
                f'{API_URL}{API_URIS["create_new_token"]}',
                headers=get_auth_api_headers(bot=bot),
                json=to_send,
                allow_redirects=True,
            )
            json_data = response.json()
            status_code = response.status_code
            if status_code == 201:
                token = json_data['tokens'][0]
                new_text = f'Новый ключ создан.\n Для копирования ключа тапните на него.\n'
                text = text_replace_for_markdown(prepare_token_to_send(token, bot))
                bot.send_message(user_id, new_text, reply_markup=main_keyboard())
                bot.send_message(user_id, text, reply_markup=main_keyboard(), parse_mode='MarkdownV2')
            elif status_code == 403:
                bot.send_message(
                    user_id,
                    "У Вас уже есть демо ключ.\nПолучение второго ключа не возможно\nВозврат в основное меню",
                    reply_markup=main_keyboard(),
                )
            elif status_code == 404 and "User does not exist" in json_data['details']:
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
    tariffs = update_tariffs(bot=bot)
    msg = ['Доступные тарифы:\n']
    for tariff in tariffs:
        if tariff["traffic_limit"]:
            limit = f'Лимит трафика: {format_bytes_to_human(tariff["traffic_limit"])}'
        else:
            limit = 'Без ограничения трафика'
        if tariff["prolong_period"]:
            prolong_period = f'срок действия в днях: {tariff["prolong_period"]}'
        else:
            prolong_period = 'без ограничения по сроку'
        if tariff["price"]:
            price = f'стоимость - {tariff["price"]} {tariff["currency"]["name"]}'
        else:
            price = 'бесплатный'
        msg.append(f'Наименование: {tariff["name"]}, '
                   f'{prolong_period}\n'
                   f'{limit}, {price}\n'
                   )
    bot.send_message(user_id, '\n'.join(msg), reply_markup=main_keyboard())


def send_wait_message_to_user(bot: TeleBot, user_id: int):
    bot.send_message(user_id, 'Ваш запрос в очереди. Ожидайте.', reply_markup=types.ReplyKeyboardRemove())

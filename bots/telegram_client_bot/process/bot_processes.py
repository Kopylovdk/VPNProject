import requests
import logging

from requests import Response
from telebot import TeleBot

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

API_CREDS_USERNAME = CONFIG['bot']['api']['username']
API_CREDS_PASSWORD = CONFIG['bot']['api']['password']
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
    log.debug(f'Health check URL={url}')
    response = requests.get(url, allow_redirects=True)
    log.debug(f'{response=!r}')
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
        log.debug(f'{response.json()=!r}, {text!r}')
    else:
        text = f'ОШИБКА ПОДКЛЮЧЕНИЯ К БЭКУ:\n' \
               f'Status_code = {response.status_code!r}\n'
        log.debug(f'{text!r}')

    for admin_id in TECH_ADMIN:
        bot.send_message(admin_id, text=text)


def send_msg_to_managers(bot: TeleBot, text: str, message: Message) -> None:
    """Функция отправки сообщений всем менеджерам"""
    for manager_id in MANAGERS:
        bot.send_message(
            manager_id,
            text=f'Пользователь:\n'
                 f'ID - {message.from_user.id!r}\n'
                 f'Логин - {message.from_user.username!r}\n'
                 f'ФИО - {message.from_user.full_name!r}\n'
                 f'{text}',
        )
        bot.forward_message(manager_id, message.chat.id, message.message_id)


def add_or_update_user(bot: TeleBot, user: User) -> None:
    to_send = {
        'transport_name': BOT_NAME,
        'credentials': user.to_dict()
    }
    response = requests.post(
        f'{API_URL}{API_URIS["creat_or_update_contact"]}',
        headers=get_auth_api_headers(bot=bot),
        json=to_send,
        allow_redirects=True,
    )
    if response.status_code not in [200, 201]:
        send_alert_to_admins(bot, response, user)
    else:
        json_response = response.json()
        log.info(f'{json_response["details"]}:\n{json_response["user_info"]}')


def get_vpn_keys(bot: TeleBot, user: User) -> None:
    to_send = {
        'transport_name': BOT_NAME,
        'messenger_id': user.id
    }
    response = requests.get(
        f'{API_URL}{API_URIS["get_client_tokens"].format(**to_send)}',
        headers=get_auth_api_headers(bot=bot),
        allow_redirects=True,
    )
    if response.status_code not in [200]:
        send_alert_to_admins(bot, response, user)
        bot.send_message(user.id, f"{SERVER_EXCEPTION}\nВозврат в основное меню", reply_markup=main_keyboard())
    else:
        log.info(f"{response.json()}")
        tokens = response.json()['tokens']
        bot.send_message(user.id, '\n'.join(tokens) if tokens else 'Ключи отсутствуют', reply_markup=main_keyboard())


def demo_token(data: dict):
    pass


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
            to_send = {
                'transport_name': BOT_NAME,
                'credentials': message.from_user.to_dict(),
                'outline_id': message.text
            }
            response = requests.post(
                f'{API_URL}{API_URIS["renew_exist_token"]}',
                headers=get_auth_api_headers(),
                json=to_send,
                allow_redirects=True,
            )
            status_code = response.status_code
            user_id = message.from_user.id
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
                bot.send_message(
                    user_id,
                    "Ключ принадлежит другому пользователю, проверьте ID ключа и повторите ввод",
                    reply_markup=back_to_main_menu_keyboard()
                )
                bot.register_next_step_handler(message, renew_token_step_2, bot)
            else:
                send_alert_to_admins(bot=bot, response=response, user=message.from_user)
                bot.send_message(user_id, f"{SERVER_EXCEPTION}\nВозврат в основное меню", reply_markup=main_keyboard())


def subscribes_step_1(message: Message, bot: TeleBot):
    available_tariffs_dicts = get_tariffs(bot=bot)
    available_tariffs_names = [data['name'] for data in available_tariffs_dicts]
    bot.send_message(
        message.chat.id,
        'Выберите подписку',
        reply_markup=generate_action_keyboard(available_tariffs_names)
    )
    bot.register_next_step_handler(message, subscribes_step_2, bot, available_tariffs_dicts, available_tariffs_names)


def subscribes_step_2(message: Message, bot: TeleBot, available_tariffs_dicts: list, available_tariffs_names: list):
    user_answer = message.text
    if user_answer in 'В основное меню':
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_keyboard())
    elif user_answer in available_tariffs_names:
        selected_tariff_dict = {}
        # for tariff_dict in available_tariffs_dicts:
        #     if tariff_dict['name'] == user_answer:
        #         selected_tariff_dict = tariff_dict
        #
        # demo_token({''})
        # bot.send_message(message.chat.id, 'В разработке', reply_markup=main_keyboard())
    # elif user_answer in ['3 месяца', '6 месяцев']:
        for tariff_dict in available_tariffs_dicts:
            if tariff_dict['name'] == user_answer:
                selected_tariff_dict = tariff_dict
        available_vpn_servers = get_vpn_servers(bot=bot)
        bot.send_message(
            message.chat.id,
            'Выберите сервер',
            reply_markup=generate_action_keyboard(available_vpn_servers),
        )
        bot.register_next_step_handler(message, subscribes_step_3, bot, selected_tariff_dict, available_vpn_servers)
    else:
        bot.send_message(message.chat.id, 'Такой подписки не существует, повторите выбор')
        bot.register_next_step_handler(message, subscribes_step_2, bot, available_tariffs_dicts, available_tariffs_names)


def subscribes_step_3(message: Message, bot: TeleBot, selected_tariff_dict: dict, available_vpn_servers: list):
    if message.text in 'В основное меню':
        bot.send_message(message.chat.id, 'Возврат в основное меню', reply_markup=main_keyboard())
    elif message.text in available_vpn_servers:
        selected_server = message.text
        send_msg_to_managers(
            bot=bot,
            message=message,
            text=f'Выбранный тариф:\n'
                 f'Наименование: {selected_tariff_dict["name"]}\n'
                 f'Срок действия: {selected_tariff_dict["prolong_period"]}\n'
                 f'Стоимость: {selected_tariff_dict["price"]}\n'
                 f'Выбранный сервер - {selected_server}',
        )
        bot.send_message(
            message.chat.id,
            'Выбранный сервер и тарифный план передан менеджеру.\nОжидайте ответ',
            reply_markup=main_keyboard(),
        )
    else:
        bot.send_message(message.chat.id, 'Такого сервера не существует, повторите выбор')
        bot.register_next_step_handler(message, subscribes_step_3, bot, selected_tariff_dict, available_vpn_servers)
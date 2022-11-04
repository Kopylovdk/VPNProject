import requests
import logging


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

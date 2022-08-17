from telebot import TeleBot
from telebot.types import Message, User
from apps.service.bot.bot_processes import (
    add_new_vpn_key_to_tg_user_step_1,
    delete_step_1,
    active_prolong_api_key_step_1,
    personal_message_send_step_1,
    all_users_message_send_step_1,
    user_vpn_keys_list_step_1,
    messages_send_choice_step_1,
)
from apps.service.processes import (
    get_all_admins,
    add_new_tg_user,
    get_all_vpn_keys_of_user,
    add_new_key, get_tg_user_by_,
)
from apps.service.bot.keyboards import main_keyboard, subscribe_keyboard, bot_message_keyboard, main_admin_keyboard
from vpnservice.settings import EXTERNAL_CFG


tg_bot_conf = EXTERNAL_CFG['tg_bot']
bot = TeleBot(tg_bot_conf['token'])


def send_msg_to_admins(user: User, text: str) -> None:
    """
    Функция отправки сообщений всем администратора
    Params:
        user: User
    Returns: None
    Exceptions: None
    """
    admin_ids = get_all_admins()
    for admin_id in admin_ids:
        bot.send_message(
            admin_id,
            text=f'Пользователь:\n'
                 f'ID - {user.id!r}\n'
                 f'Логин - {user.username!r}\n'
                 f'ФИО - {user.full_name!r}\n'
                 f'{text!r}',
        )


@bot.message_handler(commands=['start'])
def start(message: Message):
    """Хендлер команды Start"""
    tg_user = message.from_user
    bot.send_message(
        message.chat.id,
        text='Добро пожаловать в VPN Project!',
        reply_markup=main_keyboard(tg_user.id)
    )
    add_new_tg_user(tg_user)


@bot.message_handler(content_types=["text"])
def handle_text(message: Message):
    """Хендлер обработки текстовых команд клавиатуры от пользователя"""
    tg_user = message.from_user
    add_new_tg_user(tg_user)
    if 'Оформить подписку' in message.text:
        bot.send_message(
            tg_user.id,
            text='Выберите вариант подписки',
            reply_markup=subscribe_keyboard()
        )

    elif 'Демо' in message.text:
        vpn_key = add_new_key()
        vpn_key.add_traffic_limit(1024 * 1024 * 1024)
        vpn_key.add_tg_user(get_tg_user_by_(telegram_data=tg_user.id))
        vpn_key.change_active_status()
        vpn_key.change_valid_until(7)

        bot.send_message(
            message.chat.id,
            f'Ваш демо ключ: {vpn_key.outline_key_value!r}\n'
            f'Воспользуйтесь Инструкцией для дальнейшей работы с сервисом',
            reply_markup=main_keyboard(tg_user.id)
        )

    elif message.text in ['3 месяца', '6 месяцев']:
        bot.send_message(
            tg_user.id,
            text='Для оплаты подписки с Вами свяжется Администратор.',
            reply_markup=main_keyboard(tg_user.id)
        )
        send_msg_to_admins(user=tg_user, text=f'Хочет оплатить подписку на {message.text!r}')

    elif 'Мои VPN ключи' in message.text:
        vpn_keys = get_all_vpn_keys_of_user(tg_user.id)
        bot.send_message(
            tg_user.id,
            '\n'.join(vpn_keys) if vpn_keys else 'Ключи отсутствуют, если это не так - обратитесь к администратору.',
            reply_markup=main_keyboard(tg_user.id)
        )

    elif 'Инструкция' in message.text:
        with open('apps/service/bot/instructions.txt', 'r') as f:
            instruction = f.read()
        # if tg_user.id in get_all_admins():
        #     with open('apps/service/bot/instructions_admin.txt', 'r') as fa:
        #         instruction += fa.read()

        bot.send_message(
            tg_user.id,
            text=instruction,
            reply_markup=main_keyboard(tg_user.id)
        )

    elif 'Поддержка' in message.text:
        send_msg_to_admins(user=tg_user, text='Требуется помощь администратора')
        bot.send_message(
            tg_user.id,
            text='Администратор свяжется с Вами в ближайшее время.',
            reply_markup=main_keyboard(tg_user.id),
        )

    elif 'Режим администратора' in message.text:
        bot.send_message(
            tg_user.id,
            text='Режим Администратора включен',
            reply_markup=main_admin_keyboard(),
        )
    elif 'Режим пользователя' in message.text:
        bot.send_message(
            tg_user.id,
            text='Режим Администратора выключен',
            reply_markup=main_keyboard(tg_user.id),
        )
    elif 'Список ключей пользователя' in message.text:
        user_vpn_keys_list_step_1(message, bot)

    elif 'Новый ключ' in message.text:
        vpn_key = add_new_key()
        vpn_key.add_traffic_limit()
        bot.send_message(tg_user.id, f'Ключ создан с лимитом трафика в 1 кб.')
        bot.send_message(tg_user.id, f'vpn_key_id={vpn_key.outline_key_id!r}')

    elif 'Привязать ключ к пользователю' in message.text:
        add_new_vpn_key_to_tg_user_step_1(message, bot)

    elif 'Активация/продление ключа' in message.text:
        active_prolong_api_key_step_1(message, bot)

    elif 'Отправка сообщений' in message.text:
        messages_send_choice_step_1(message, bot)

    elif 'Удалить ключ' in message.text:
        delete_step_1(message, bot)

    elif 'В основное меню' in message.text:
        bot.send_message(tg_user.id, 'Возврат в основное меню', reply_markup=main_keyboard(tg_user.id))
    else:
        bot.send_message(
            tg_user.id,
            text='Такой команды не существует.',
            reply_markup=main_keyboard(tg_user.id)
        )

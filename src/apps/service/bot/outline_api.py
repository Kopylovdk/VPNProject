from outline_vpn.outline_vpn import OutlineVPN, OutlineKey
from telebot import TeleBot
from telebot.types import Message
from keyboards import one_time_keyboard_yes_no, one_time_keyboard_cancel, main_keyboard
from vpnservice.settings import EXTERNAL_CFG


outline_conf = EXTERNAL_CFG['outline_vpn']
outline_client = OutlineVPN("https://{}:{}/{}".format(*outline_conf.values()))


def create_new_vpn_key() -> OutlineKey:
    """Метод создания нового ключа
    Params: None
    Returns: OutlineKey
    Exceptions: None
    """
    return outline_client.create_key()

#
# def keys_list(client: OutlineVPN):
#     """Метод получения списка ключей
#     Params:
#         client: OutlineVPN
#     Returns:
#         str
#     Exceptions: None
#     """
#     keys = client.get_keys()
#     text_to_send = []
#     for key in keys:
#         # text_to_send.append(f'id: {key.key_id!r}, имя: {key.name!r}, ключ доступа:{key.access_url!r}, '
#         #                     f'valid until: {key.valid_until}')
#         text_to_send.append(f'id: {key.key_id!r}, имя: {key.name!r}, valid until: {key.valid_until}')
#     return '\n'.join(text_to_send)


# def delete_step_1(message: Message, bot: TeleBot, client: OutlineVPN):
#     message = bot.reply_to(
#         message,
#         "Вы хотите УДАЛИТЬ ключ?\n"
#         "Если да, то на следующем шаге укажите ID ключа\n"
#         "Если Вы не знаете ID - то посмотреть его можно получив весь список ключей",
#         reply_markup=one_time_keyboard_yes_no()
#     )
#     bot.register_next_step_handler(message, delete_step_2, bot, client)
#
#
# def delete_step_2(message: Message, bot: TeleBot, client: OutlineVPN):
#     if message.text == 'да':
#         message = bot.send_message(
#             message.chat.id, f"Введите id ключа для удаления.",
#             reply_markup=one_time_keyboard_cancel()
#         )
#         bot.register_next_step_handler(message, delete_step_3, bot, client)
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
# def delete_step_3(message: Message, bot: TeleBot, client: OutlineVPN):
#     if message.text == 'отмена':
#         bot.send_message(message.chat.id, 'Возврат в основное меню.', reply_markup=admin_keyboard())
#     else:
#         bot.send_message(message.chat.id, delete_key(client, message.text))
#         bot.send_message(message.chat.id, 'Возврат в основное меню.', reply_markup=admin_keyboard())


# def delete_key(client: OutlineVPN, key_id: int) -> str:
#     """Метод удаления ключа
#     Params:
#         client: OutlineVPN
#         key_id: int
#     Returns:
#         str
#     Exceptions: None
#     """
#     response = client.delete_key(key_id)
#     if response:
#         return f'Ключ {key_id!r} удален.'
#     return f'Ошибка удаления ключа {key_id!r}. Проверьте корректность id.'

#
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
#
# def name_add(client: OutlineVPN, key_id: int, key_name: str) -> str:
#     """Метод переименования ключей
#     Params:
#         client: OutlineVPN
#         key_id: int
#         key_name: str
#     Returns:
#         str
#     Exceptions: None
#     """
#     response = client.rename_key(key_id, key_name)
#     if response:
#         return f'Имя {key_name!r} успешно добавлено для ID {key_id!r}.'
#     return f'Ошибка добавления имени ключа для ID {key_id!r}. Проверьте корректность.'

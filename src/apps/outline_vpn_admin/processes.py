import datetime
import logging
from copy import copy
from apps.outline_vpn_admin import exceptions
from apps.outline_vpn_admin.models import (
    Client,
    Contact,
    Transport,
    VPNToken,
    VPNServer,
    Tariff,
)
from apps.outline_vpn_admin.outline_api import get_outline_client
from vpnservice.settings import DEMO_KEY_PERIOD, DEMO_TRAFFIC_LIMIT

log = logging.getLogger(__name__)


def get_transport_contact_by_(
    transport_name: str,
    credentials: dict = None,
    messenger_id: int = None,
) -> Transport and Contact:
    try:
        transport = Transport.objects.get(name=transport_name)
    except Transport.DoesNotExist:
        raise exceptions.TransportDoesNotExist(message=f'Bot {transport_name!r} does not exist')

    if credentials:
        check_uid = transport.make_contact_credentials_uid(credentials)
    else:
        check_uid = transport.make_contact_messenger_id_uid(messenger_id)

    contacts = transport.contact_set

    try:
        contact = contacts.get(uid=check_uid)
    except Contact.DoesNotExist:
        raise exceptions.UserDoesNotExist(message=f'User does not exist')
    return transport, contact


def create_or_update_contact(transport_name: str, credentials: dict) -> dict:
    response = {}
    try:
        transport, contact = get_transport_contact_by_(transport_name=transport_name, credentials=credentials)
    except exceptions.UserDoesNotExist:
        transport = Transport.objects.get(name=transport_name)
        client = Client()
        transport.fill_client_details(client, credentials)
        contact = Contact.objects.create(
            client=client,
            transport=transport,
            credentials=credentials,
        )
        response['details'] = 'Created new user'
    else:
        contact.credentials = credentials
        response['details'] = 'Updated exist user'

    contact.save()
    response["user_info"] = {
            "user": contact.client.as_dict(),
            "contact": contact.as_dict()
        }

    return response


def get_client_tokens(transport_name: str, messenger_id: int) -> dict:
    transport, contact = get_transport_contact_by_(transport_name=transport_name, messenger_id=messenger_id)

    client = contact.client
    response = {
        "details": "client_tokens",
        "tokens": [token.as_dict(exclude=['id']) for token in VPNToken.objects.filter(client=client)],
        "user_info": {
            "user": contact.client.as_dict(),
            "contact": contact.as_dict(),
        },
    }
    return response


def get_client(transport_name: str, messenger_id: int) -> dict:
    transport, contact = get_transport_contact_by_(transport_name=transport_name, messenger_id=messenger_id)
    response = {
        "details": "get_client",
        "user_info": {
            "user": contact.client.as_dict(),
            "contact": contact.as_dict(),
        },
    }
    return response


def token_new(
    transport_name: str,
    server_name: str,
    credentials: dict
) -> dict:

    transport, contact = get_transport_contact_by_(transport_name=transport_name, credentials=credentials)
    try:
        vpn_server = VPNServer.objects.get(name=server_name)
    except VPNServer.DoesNotExist:
        raise exceptions.VPNServerDoesNotExist(message=f'VPN Server {server_name!r} does not exist')
    else:
        outline_client = get_outline_client(vpn_server.name)
        outline_key = outline_client.create_key()
        outline_key_name = f"OUTLINE_VPN_id:{outline_key.key_id!r}, uid: {contact.uid!r}"
        outline_client.rename_key(outline_key.key_id, outline_key_name)

        new_token = VPNToken(
            client=contact.client,
            server=vpn_server,
            outline_id=outline_key.key_id,
            vpn_key=outline_key.access_url,
            name=outline_key_name,
        )
        new_token.save()
        response = {
            "details": "new_token",
            "tokens": [new_token.as_dict(exclude=['id'])],
            "user_info": {
                "user": contact.client.as_dict(),
                "contact": contact.as_dict(),
            },
        }
        return response


def token_renew(
    transport_name: str,
    server_name: str,
    credentials: dict,
    token_id: int
) -> dict:
    transport, contact = get_transport_contact_by_(transport_name=transport_name, credentials=credentials)

    old_token = VPNToken.objects.get(outline_id=token_id)

    outline_client = get_outline_client(server_name)
    new_outline_key = outline_client.create_key()
    outline_key_name = f"OUTLINE_VPN_id:{new_outline_key.key_id!r}, uid: {contact.uid!r}"
    outline_client.rename_key(new_outline_key.key_id, outline_key_name)

    new_token = copy(old_token)
    new_token.id = None
    new_token.outline_id = new_outline_key.key_id
    new_token.name = outline_key_name
    new_token.vpn_key = new_outline_key.access_url
    new_token.save()

    old_token.is_active = False
    old_token.name = "DELETED"
    old_token.save()
    outline_client.delete_key(old_token.outline_id)

    response = {
        "details": "renew_token",
        "tokens": [new_token.as_dict(exclude=['id'])],
        "user_info": {
            "user": contact.client.as_dict(),
            "contact": contact.as_dict(),
        },
    }

    return response


def token_demo(
    transport_name: str,
    server_name: str,
    credentials: dict
) -> dict:
    transport, contact = get_transport_contact_by_(transport_name=transport_name, credentials=credentials)
    if contact.client.is_has_demo():
        raise exceptions.DemoKeyExist(message=f'User {contact.client!r} already have demo key')
    try:
        vpn_server = VPNServer.objects.get(name=server_name)
    except VPNServer.DoesNotExist:
        raise exceptions.VPNServerDoesNotExist(message=f'VPN Server {server_name!r} does not exist')
    else:
        outline_client = get_outline_client(vpn_server.name)
        outline_key = outline_client.create_key()
        outline_key_name = f"OUTLINE_VPN_id:{outline_key.key_id!r}, uid: {contact.uid!r}"
        outline_client.rename_key(outline_key.key_id, outline_key_name)
        outline_client.add_data_limit(outline_key.key_id, DEMO_TRAFFIC_LIMIT)

        demo_token = VPNToken(
            client=contact.client,
            server=vpn_server,
            outline_id=outline_key.key_id,
            vpn_key=outline_key.access_url,
            name=outline_key_name,
            traffic_limit=DEMO_TRAFFIC_LIMIT,
            valid_until=datetime.datetime.now() + datetime.timedelta(days=DEMO_KEY_PERIOD),
            is_demo=True,
        )
        demo_token.save()
        response = {
            "details": "demo_token",
            "tokens": [demo_token.as_dict(exclude=['id'])],
            "user_info": {
                "user": contact.client.as_dict(),
                "contact": contact.as_dict(),
            },
        }
        return response


def get_tariff() -> dict:
    response = {
        "details": "get_tariff",
        "tariffs": [],
    }
    for tariff in Tariff.objects.filter(is_active=True):
        to_dict_tariff = tariff.as_dict(exclude=['is_active', 'id', 'valid_until', 'prolong_days'])
        response["tariffs"].append(to_dict_tariff)
    return response


# TODO: add tests
def get_vpn_servers() -> dict:
    response = {
        "details": "get_vpn_servers",
        "vpn_servers": [],
    }
    for vpn_server in VPNServer.objects.filter(is_active=True):
        response["vpn_servers"].append(vpn_server.name)
    return response


# TODO: Переделать под новые реалии
# def get_all_admins() -> list[int]:
#     """
#     Функция получения Telegram_id ВСЕХ администраторов
#     Params: None
#     Returns:
#         list[int]
#     Exceptions: None
#     """
#     return list(TelegramUsers.objects.filter(is_admin=True).values_list('telegram_id', flat=True))
#
#
# def get_all_no_admin_users() -> list[int]:
#     """
#     Функция получения Telegram_id ВСЕХ обычных пользователей
#     Params: None
#     Returns: list[int]
#     Exceptions: None
#     """
#     return list(TelegramUsers.objects.filter(is_admin=False).values_list('telegram_id', flat=True))
#

# def add_traffic_limit(vpn_server_name: str, obj: OutlineVPNKeys, limit_in_bytes: int = 1024) -> bool:
#     """
#     Метод установки лимита трафика на запись OutlineVPNKeys
#     Params:
#         limit_in_bytes: int = 1024
#         test: bool = False - используется для мока запроса на сервер outline
#     Returns: none
#     Exceptions: None
#     """
#     outline_client = get_outline_client(vpn_server_name)
#     response = outline_client.add_data_limit(obj.outline_key_id, limit_in_bytes)
#     if not response:
#         return response
#     obj.outline_key_traffic_limit = limit_in_bytes
#     obj.save()
#     return response
#
#
# def del_traffic_limit(vpn_server_name: str, obj: OutlineVPNKeys) -> bool:
#     """
#     Метод удаления лимита трафика с записи OutlineVPNKeys
#     Params:
#         test: bool = False - используется для мока запроса на сервер outline
#     Returns: none
#     Exceptions: None
#     """
#     outline_client = get_outline_client(vpn_server_name)
#     response = outline_client.delete_data_limit(obj.outline_key_id)
#     if not response:
#         return response
#     obj.outline_key_traffic_limit = None
#     obj.save()
#     return response
#
#
# def del_outline_vpn_key(vpn_server_name: str, obj: OutlineVPNKeys) -> bool:
#     outline_client = get_outline_client(vpn_server_name)
#     response = outline_client.delete_key(obj.outline_key_id)
#     if not response:
#         return response
#     obj.delete()
#
#     return response
#
#
# def change_outline_vpn_key_name(vpn_server_name: str, obj: OutlineVPNKeys, name: str) -> bool:
#     outline_client = get_outline_client(vpn_server_name)
#     response = outline_client.rename_key(obj.outline_key_id, name)
#     if not response:
#         return response
#     obj.outline_key_name = name
#     obj.save()
#     return response

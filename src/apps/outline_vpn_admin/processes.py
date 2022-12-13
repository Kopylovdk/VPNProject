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
from vpnservice.settings import DATE_STRING_FORMAT


log = logging.getLogger(__name__)


def get_transport_contact_by_(
        transport_name: str,
        credentials: dict = None,
        messenger_id: int = None,
) -> Transport and Contact:
    try:
        transport = Transport.objects.get(name=transport_name)
    except Transport.DoesNotExist as err:
        log.error(f'Error get_transport_contact_by_ {transport_name=!r}, {credentials=!r}, {messenger_id=!r}, {err=!r}')
        raise exceptions.TransportDoesNotExist(message=f'Bot {transport_name!r} does not exist')

    if credentials:
        check_uid = transport.make_contact_credentials_uid(credentials)
    else:
        check_uid = transport.make_contact_messenger_id_uid(messenger_id)

    contacts = transport.contact_set

    try:
        contact = contacts.get(uid=check_uid)
    except Contact.DoesNotExist as err:
        log.error(f'Error get_transport_contact_by_ {transport_name=!r}, {credentials=!r}, {messenger_id=!r}, {err=!r}')
        raise exceptions.UserDoesNotExist(message=f'User does not exist')
    return transport, contact


def create_or_update_contact(
    transport_name: str,
    credentials: dict,
) -> dict:
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
            phone_number=credentials['phone_number'] if credentials['phone_number'] else None
        )
        response['details'] = 'Created new user'
    else:
        contact.credentials = credentials
        contact.phone_number = credentials['phone_number'] if credentials['phone_number'] else None
        response['details'] = 'Updated exist user'

    contact.save()
    response["user_info"] = {
        "user": contact.client.as_dict(),
        "contact": contact.as_dict()
    }
    log.debug(f"{response['details']} - {response}")
    return response


def get_client_tokens(transport_name: str, messenger_id: int) -> dict:
    transport, contact = get_transport_contact_by_(transport_name=transport_name, messenger_id=messenger_id)
    log.debug(f'get_client_tokens - {transport=!r}, {contact=!r}')

    client = contact.client

    response = {
        "details": "client_tokens",
        "tokens": [],
        "user_info": {
            "user": client.as_dict(),
            "contact": contact.as_dict(),
        },
    }

    for token in client.vpntoken_set.filter(is_active=True):
        token_dict = token.as_dict()
        if token_dict['valid_until']:
            token_dict['valid_until'] = token_dict['valid_until'].strftime(DATE_STRING_FORMAT)
        response["tokens"].append(token_dict)

    log.debug(f'get_client_tokens result- {response=!r}')
    return response


def get_client(
    transport_name: str,
    messenger_id: int,
) -> dict:
    transport, contact = get_transport_contact_by_(transport_name=transport_name, messenger_id=messenger_id)
    log.debug(f'get_client start - {transport=!r}, {contact=!r}')
    response = {
        "details": "get_client",
        "user_info": {
            "user": contact.client.as_dict(),
            "contact": contact.as_dict(),
        },
    }
    log.debug(f'get_client result - {response=!r}')
    return response


def token_new(
    server_name: str,
    tariff_name: str,
    transport_name: str = None,
    credentials: dict = None,
) -> dict:

    try:
        vpn_server = VPNServer.objects.get(name=server_name)

    except VPNServer.DoesNotExist as err:
        log.error(f'Error token_new {transport_name=!r}, {credentials=!r}, {server_name=!r}, {err=!r}')
        raise exceptions.VPNServerDoesNotExist(message=f'VPN Server {server_name!r} does not exist')

    outline_client = get_outline_client(vpn_server)

    try:
        tariff = Tariff.objects.get(name=tariff_name)
    except Tariff.DoesNotExist as err:
        log.error(
            f'Error token_new {tariff_name=!r}, {transport_name=!r}, {credentials=!r}, {server_name=!r}, {err=!r}')
        raise exceptions.TariffDoesNotExist(message=f'Tariff {tariff_name!r} does not exist')

    response = {}
    if transport_name and credentials:
        transport, contact = get_transport_contact_by_(transport_name=transport_name, credentials=credentials)
        if tariff.is_demo and contact.client.is_has_demo():
            err = f'User already have demo key'
            log.debug(f'Error token_new {tariff=!r}, {transport_name=!r}, {credentials=!r}, {server_name=!r}, {err=!r}')
            raise exceptions.DemoKeyExist(message=err)
        client = contact.client
        response["details"] = 'new_token by client'
        response["user_info"] = {
            "user": client.as_dict(),
            "contact": contact.as_dict(),
        }
    else:
        if tariff.is_demo:
            err = f'Cannot create demo key from admin'
            log.debug(f'Error token_new {tariff=!r}, {transport_name=!r}, {credentials=!r}, {server_name=!r}, {err=!r}')
            raise exceptions.DemoKeyNotAllowed(message=err)
        client = Client()
        client.save()
        response["details"] = 'new_token by admin'
        response["user_info"] = {
            "user": client.as_dict(),
            "contact": '',
        }

    outline_key = outline_client.create_key()
    outline_key_name = f"OUTLINE_VPN_id:{outline_key.key_id!r}, client_id: {client.id!r}"
    outline_client.rename_key(outline_key.key_id, outline_key_name)
    outline_client.add_data_limit(outline_key.key_id, tariff.traffic_limit)

    valid_until = None
    if tariff.prolong_period:
        valid_until = datetime.datetime.now() + datetime.timedelta(days=tariff.prolong_period)
    new_token = VPNToken(
        client=client,
        server=vpn_server,
        outline_id=outline_key.key_id,
        vpn_key=outline_key.access_url,
        name=outline_key_name,
        tariff=tariff,
        traffic_limit=tariff.traffic_limit,
        valid_until=valid_until,
    )
    if tariff.is_demo:
        new_token.is_demo = True
    if tariff.is_tech:
        new_token.is_tech = True
    new_token.save()
    token_dict = new_token.as_dict()
    if token_dict['valid_until']:
        token_dict['valid_until'] = token_dict['valid_until'].strftime(DATE_STRING_FORMAT)
    response["tokens"] = [token_dict]
    return response


def token_renew(
    token_id: int,
    transport_name: str = None,
    credentials: dict = None,
) -> dict:
    response = {}
    if transport_name and credentials:
        transport, contact = get_transport_contact_by_(transport_name=transport_name, credentials=credentials)
        client = contact.client
        log.debug(f'{transport=!r}, {contact=!r}, {client=!r}')
        if not client.is_token_owner(token_id):
            err = f'Error token renew. Token belongs to another user.'
            log.error(err)
            raise exceptions.BelongToAnotherUser(message=err)
        old_token = client.vpntoken_set.get(id=token_id)
        old_token_name_prefix = 'Renewed by client'
        response["user_info"] = {
            "user": client.as_dict(),
            "contact": contact.as_dict(),
        }
        response["details"] = "renew_token by client"
    else:
        old_token = get_token(token_id)
        old_token_name_prefix = 'Renewed by admin'
        response["user_info"] = {
            "user": old_token.client.as_dict(),
            "contact": '',
        }
        response["details"] = "renew_token by admin"
    if old_token.is_demo:
        err = f'Error token renew. Cannot renew demo key.'
        log.error(err)
        raise exceptions.DemoKeyNotAllowed(message=err)

    outline_client = get_outline_client(old_token.server)
    new_outline_key = outline_client.create_key()
    outline_key_name = f"OUTLINE_VPN_id:{new_outline_key.key_id!r}, client_id: {old_token.client.id!r}"
    outline_client.rename_key(new_outline_key.key_id, outline_key_name)

    new_token = copy(old_token)
    new_token.id = None
    new_token.previous_vpn_token_id = old_token.id
    new_token.outline_id = new_outline_key.key_id
    new_token.name = outline_key_name
    new_token.vpn_key = new_outline_key.access_url
    new_token.save()

    old_token.is_active = False
    old_token.name = f'{old_token_name_prefix} {old_token.name}'
    old_token.save()
    outline_client.delete_key(old_token.outline_id)
    new_token_dict = new_token.as_dict()

    if new_token_dict['valid_until']:
        new_token_dict['valid_until'] = new_token_dict['valid_until'].strftime(DATE_STRING_FORMAT)
    response["tokens"] = [new_token_dict]
    return response


def get_tariff() -> dict:
    response = {
        "details": "get_tariff",
        "tariffs": [],
    }
    for tariff in Tariff.objects.select_related('currency').filter(is_active=True):
        currency_dict = tariff.currency.as_dict(exclude=['is_active'])
        currency_dict['exchange_rate'] = str(currency_dict['exchange_rate'])
        tariff_dict = tariff.as_dict(exclude=['is_active', 'valid_until'])
        tariff_dict['price'] = str(tariff_dict['price'])
        tariff_dict['currency'] = currency_dict
        response["tariffs"].append(tariff_dict)
    return response


def get_vpn_servers() -> dict:
    response = {
        "details": "get_vpn_servers",
        "vpn_servers": [],
    }
    for vpn_server in VPNServer.objects.filter(is_active=True):
        add_to_dict = vpn_server.as_dict(exclude=['is_active', 'uri', 'is_default'])
        response["vpn_servers"].append(add_to_dict)
    return response


def get_transports() -> dict:
    response = {
        "details": "get_bots",
        "transports": [],
    }
    for transport in Transport.objects.filter(is_active=True):
        response["transports"].append(transport.as_dict(exclude=['credentials']))
    return response


def get_token(token_id: int) -> VPNToken:
    try:
        return VPNToken.objects.select_related('server', 'client').get(id=token_id)
    except VPNToken.DoesNotExist as err:
        raise exceptions.VPNTokenDoesNotExist(message=f'VPN Token id={token_id!r} does not exist, {err=!r}')


def get_token_info(token_id: int) -> dict:
    vpn_token_dict = get_token(token_id).as_dict()
    if vpn_token_dict['valid_until']:
        vpn_token_dict['valid_until'] = vpn_token_dict['valid_until'].strftime(DATE_STRING_FORMAT)
    return {'details': 'get_token_info', 'tokens': [vpn_token_dict]}


def add_traffic_limit(token_id: int, traffic_limit: int = 1024) -> dict:
    vpn_token = get_token(token_id)
    outline_client = get_outline_client(vpn_token.server)
    limit_in_bytes = traffic_limit * 1024 * 1024
    response = outline_client.add_data_limit(vpn_token.outline_id, limit_in_bytes)
    if not response:
        msg = 'Outline client error occurred due traffic limit add'
        log.error(msg)
        raise exceptions.VPNServerResponseError(message=msg)
    vpn_token_dict = change_vpn_token_traffic_limit(vpn_token, traffic_limit)
    return {'details': 'Traffic limit updated', 'tokens': [vpn_token_dict]}


def del_traffic_limit(token_id: int) -> dict:
    vpn_token = get_token(token_id)
    outline_client = get_outline_client(vpn_token.server)
    response = outline_client.delete_data_limit(vpn_token.outline_id)
    if not response:
        msg = 'Outline client error occurred due traffic limit delete'
        log.error(msg)
        raise exceptions.VPNServerResponseError(message=msg)
    vpn_token_dict = change_vpn_token_traffic_limit(vpn_token)
    return {'details': 'Traffic limit removed', 'tokens': [vpn_token_dict]}


def change_vpn_token_traffic_limit(vpn_token: VPNToken, traffic_limit: int = None) -> dict:
    if traffic_limit:
        limit_in_bytes = traffic_limit * 1024 * 1024
        vpn_token.traffic_limit = limit_in_bytes
    else:
        vpn_token.traffic_limit = None
    vpn_token.save()
    vpn_token_dict = vpn_token.as_dict()
    if vpn_token_dict['valid_until']:
        vpn_token_dict['valid_until'] = vpn_token_dict['valid_until'].strftime(DATE_STRING_FORMAT)
    return vpn_token_dict


def del_outline_vpn_key(token_id: int) -> dict:
    vpn_token = get_token(token_id)
    outline_client = get_outline_client(vpn_token.server)
    response = outline_client.delete_key(vpn_token.outline_id)
    if not response:
        msg = 'Outline client error occurred due key delete'
        log.error(msg)
        raise exceptions.VPNServerResponseError(message=msg)
    vpn_token_dict = change_vpn_token_active_state(vpn_token)
    return {'details': 'VPN Token deleted', 'tokens': [vpn_token_dict]}


def change_vpn_token_active_state(vpn_token: VPNToken) -> dict:
    if vpn_token.is_active:
        vpn_token.is_active = False
        vpn_token.name = f'Deleted {vpn_token.name}'
        vpn_token.save()
    vpn_token_dict = vpn_token.as_dict()
    if vpn_token_dict['valid_until']:
        vpn_token_dict['valid_until'] = vpn_token_dict['valid_until'].strftime(DATE_STRING_FORMAT)
    return vpn_token_dict


def telegram_message_sender(
    transport_name: str,
    text: str,
    messenger_id: int = None,
) -> dict:
    try:
        transport = Transport.objects.get(name=transport_name)
    except Transport.DoesNotExist as err:
        log.error(f'{transport_name=!r}, {err=!r}')
        raise exceptions.TransportDoesNotExist(message=f'Bot {transport_name!r} does not exist')

    from telebot import TeleBot
    bot_creds = transport.credentials
    bot = TeleBot(bot_creds['token'])
    response = {
        'details': str,
        'info': {
            'error': 0,
            'success': 0,
        }
    }
    if messenger_id:
        log.info(f'{transport_name=!r}, {text=!r}, {messenger_id=!r}')
        response['details'] = 'Personal message send'
        try:
            bot.send_message(messenger_id, text)
        except Exception as err:
            msg = f'{transport_name=!r}, {err=!r}'
            log.error(msg)
            raise exceptions.TransportMessageSendError(message=msg)
        else:
            response['info']['success'] += 1
    else:
        contacts_to_send = Contact.objects.select_related('transport').filter(transport=transport)
        response['details'] = 'All bot users message send'
        for contact in contacts_to_send:
            id_to_send = contact.uid.split('@')[1]
            try:
                bot.send_message(id_to_send, text)
            except Exception as err:
                msg = f'{transport_name=!r}, {contact!r}, {err=!r}'
                log.error(msg)
                response['info']['error'] += 1
                continue
            else:
                response['info']['success'] += 1
    return response


def update_token_valid_until(token_id: int, valid_until: int) -> dict:
    token = get_token(token_id)
    if valid_until:
        token.valid_until = datetime.datetime.now() + datetime.timedelta(days=valid_until)
    else:
        token.valid_until = None
    token.save()
    vpn_token_dict = token.as_dict()
    if vpn_token_dict['valid_until']:
        vpn_token_dict['valid_until'] = vpn_token_dict['valid_until'].strftime(DATE_STRING_FORMAT)
    return {'details': "Token valid_until updated", 'tokens': [vpn_token_dict]}


# def get_statistic_info(server_name: str):
#     # TODO
#     client = get_outline_client(server_name)
#     response = client.get_keys()
#     to_excel = {
#         'key_id': [],
#         'name': [],
#         'used_bytes': [],
#     }
#     for key in response:
#         to_excel['key_id'].append(key.key_id)
#         to_excel['name'].append(key.name)
#         to_excel['used_bytes'].append(key.used_bytes)

    # from pandas import DataFrame

    # OutlineKey(key_id='7', name="OUTLINE_VPN_id:'7', uid: 'test_client_telegram_bot@480629416'",
    #            password='t8YdfB1IrVZj', port=37877, method='chacha20-ietf-poly1305',
    #            access_url='ss://Y2hhY2hhMjAtaWV0Zi1wb2x5MTMwNTp0OFlkZkIxSXJWWmo@62.113.111.75:37877/?outline=1',
    #            used_bytes=None)

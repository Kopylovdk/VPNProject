import datetime
from apps.outline_vpn_admin.models import (
    Client,
    Contact,
    Transport,
    VPNToken,
    VPNServer,
    Tariffication,
)
TRANSPORT_CREDENTIALS = {"token": "Some token", "URL": "Any"}
CONTACT_CREDENTIALS = {"messenger_id": 'Some client ID', "Any_data": "Any_data"}


def create_client(cnt: int = 1) -> list[Client]:
    """
    Функция создания записей в таблице Client
    """
    result = []
    for obj_cnt in range(1000, cnt + 1000):
        new_obj = Client(
            full_name=f'test {obj_cnt}',
        )
        new_obj.save()
        result.append(new_obj)
    return result


def create_transport(cnt: int = 1) -> list[Transport]:
    """
    Функция создания записей в таблице Transport
    """
    result = []
    for obj_cnt in range(1000, cnt + 1000):
        new_obj = Transport(
            name=f'test {obj_cnt}',
            credentials=TRANSPORT_CREDENTIALS
        )
        new_obj.save()
        result.append(new_obj)
    return result


def create_contact(cnt: int = 1) -> list[Contact]:
    """
    Функция создания записей в таблице Contact
    """
    result = []
    clients = create_client(cnt)
    transports = create_transport(cnt)
    for _, obj_cnt in enumerate(range(1000, cnt + 1000)):
        new_obj = Contact(
            client=clients[_],
            transport=transports[_],
            name=f'test {obj_cnt}',
            credentials=CONTACT_CREDENTIALS,
        )
        new_obj.save()
        result.append(new_obj)
    return result


def create_vpn_server(cnt: int = 1) -> list[VPNServer]:
    """
    Функция создания записей в таблице VPNServer
    """
    result = []
    for obj_cnt in range(1000, cnt + 1000):
        new_obj = VPNServer(
            name=f'test {obj_cnt}',
            uri=f'test {obj_cnt}',
        )
        new_obj.save()
        result.append(new_obj)
    return result


def create_vpn_token(cnt: int = 1) -> list[VPNToken]:
    """
    Функция создания записей в таблице VPNToken
    """
    result = []
    clients = create_client(cnt)
    servers = create_vpn_server(cnt)
    for _, obj_cnt in enumerate(range(1000, cnt + 1000)):
        new_obj = VPNToken(
            client=clients[_],
            server=servers[_],
            outline_id=obj_cnt,
            name=f'test {obj_cnt}',
            vpn_key=f'test {obj_cnt}',
        )
        new_obj.save()
        result.append(new_obj)
    return result


def create_tariffication(cnt: int = 1) -> list[Tariffication]:
    """
    Функция создания записей в таблице Tariffication
    """
    result = []
    for obj_cnt in range(1000, cnt + 1000):
        new_obj = Tariffication(
            name=f'test {obj_cnt}',
            prolong_days=obj_cnt,
            price=obj_cnt * 1000,
            valid_until=datetime.datetime.now() + datetime.timedelta(days=365)
        )
        new_obj.save()
        result.append(new_obj)
    return result

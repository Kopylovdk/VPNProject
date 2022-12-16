import datetime
from apps.outline_vpn_admin.models import (
    Client,
    Contact,
    Transport,
    VPNToken,
    VPNServer,
    Tariff,
    Currency,
)
TRANSPORT_CREDENTIALS = {"token": "Some token", "URL": "Any"}
CONTACT_CREDENTIALS = {"id": "some_id", "first_name": "some_first_name", "last_name": "some_last_name", "phone_number": ''}


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


def create_transport(cnt: int = 1, transport_name: str = None) -> list[Transport]:
    """
    Функция создания записей в таблице Transport
    """
    if not transport_name:
        transport_name = "test"

    result = []
    for obj_cnt in range(1000, cnt + 1000):
        new_obj = Transport(
            name=transport_name,
            credentials=TRANSPORT_CREDENTIALS,
            uid_format='{id}',
            full_name_format='{first_name} {last_name}'
        )
        new_obj.save()
        result.append(new_obj)
    return result


def create_contact(client: Client, transport: Transport, credentials: dict = None, cnt: int = 1) -> list[Contact]:
    """
    Функция создания записей в таблице Contact
    """
    if not credentials:
        credentials = CONTACT_CREDENTIALS
    result = []
    for obj_cnt in range(1000, cnt + 1000):
        new_obj = Contact(
            client=client,
            transport=transport,
            uid=transport.make_contact_credentials_uid(credentials),
            phone_number=credentials['phone_number'] if credentials['phone_number'] else None,
            credentials=credentials,
        )
        new_obj.save()
        result.append(new_obj)
    return result


def create_vpn_server(cnt: int = 1, server_name: str = None) -> list[VPNServer]:
    """
    Функция создания записей в таблице VPNServer
    """
    result = []
    for obj_cnt in range(1000, cnt + 1000):
        server_name = server_name or f'test {obj_cnt}'
        external_name = server_name
        new_obj = VPNServer(
            name=server_name,
            external_name=external_name,
            uri=f'test {obj_cnt}',
        )
        new_obj.save()
        result.append(new_obj)
    return result


def create_vpn_token(client: Client, vpn_server: VPNServer, tariff: Tariff, cnt: int = 1) -> list[VPNToken]:
    """
    Функция создания записей в таблице VPNToken
    """
    result = []
    for obj_cnt in range(1000, cnt + 1000):
        new_obj = VPNToken(
            client=client,
            server=vpn_server,
            tariff=tariff,
            outline_id=obj_cnt,
            name=f'test {obj_cnt}',
            vpn_key=f'test {obj_cnt}',
        )
        new_obj.save()
        result.append(new_obj)
    return result


def create_tariff(currency: Currency, cnt: int = 1) -> list[Tariff]:
    """
    Функция создания записей в таблице Tariff
    """
    result = []
    for obj_cnt in range(1000, cnt + 1000):
        new_obj = Tariff(
            name=f'test {obj_cnt}',
            prolong_period=obj_cnt,
            traffic_limit=obj_cnt,
            currency=currency,
            price=obj_cnt * 1000,
            valid_until=datetime.datetime.now() + datetime.timedelta(days=365)
        )
        new_obj.save()
        result.append(new_obj)
    return result


def create_currency() -> list[Currency]:
    result = []
    name = ['ts1', 'ts2', 'ts3']
    name_iso = [111, 222, 333]
    for obj_cnt in range(len(name)):
        new_obj = Currency(
            name=name[obj_cnt],
            name_iso=name_iso[obj_cnt],
            exchange_rate=1,
            is_main=True if obj_cnt == 0 else False
        )
        new_obj.save()
        result.append(new_obj)
    return result

# if needed - uncomment and modify
# def create_token_process(cnt: int = 1) -> list[TokenProcess]:
#     result = []
#     for obj_cnt in range(cnt):
#         new_obj = TokenProcess(
#             vpn_token=,
#             transport=,
#             contact=,
#             vpn_server=,
#             script_name=,
#             text=,
#         )
#         new_obj.save()
#         result.append(new_obj)
#     return result

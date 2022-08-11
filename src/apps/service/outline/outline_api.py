from outline_vpn.outline_vpn import OutlineVPN, OutlineKey
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


def keys_list():
    """Метод получения списка ключей
    Params: None
    Returns:
        str
    Exceptions: None
    """
    return outline_client.get_keys()


def delete_key(key_id: int) -> str:
    """Метод удаления ключа
    Params:
        key_id: int
    Returns:
        str
    Exceptions: None
    """
    response = outline_client.delete_key(key_id)
    if response:
        return f'Ключ {key_id!r} удален.'
    return f'Ошибка удаления ключа {key_id!r}.'


def name_add(key_id: int, key_name: str) -> str:
    """Метод переименования ключей
    Params:
        key_id: int
        key_name: str
    Returns:
        str
    Exceptions: None
    """
    response = outline_client.rename_key(key_id, key_name)
    if response:
        return f'Имя {key_name!r} успешно добавлено для ID {key_id!r}.'
    return f'Ошибка добавления имени ключа для ID {key_id!r}. Проверьте корректность.'




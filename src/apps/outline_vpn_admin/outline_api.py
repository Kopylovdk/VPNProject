from outline_vpn.outline_vpn import OutlineVPN
from vpnservice.settings import EXTERNAL_CFG


def get_outline_client(vpn_server_name: str) -> OutlineVPN:
    return OutlineVPN(EXTERNAL_CFG['outline_vpn_urls'][f'{vpn_server_name}'])

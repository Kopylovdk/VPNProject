from outline_vpn.outline_vpn import OutlineVPN
from apps.outline_vpn_admin.models import VPNServer
from apps.outline_vpn_admin.exceptions import VPNServerDoesNotExist, VPNServerDoesNotResponse


def get_outline_client(vpn_server_name: str = None) -> OutlineVPN:
    try:
        if vpn_server_name:
            outline_client = OutlineVPN(VPNServer.objects.get(name=vpn_server_name).uri)
        else:
            outline_client = OutlineVPN(VPNServer.objects.get(is_default=True).uri)
    except VPNServer.DoesNotExist:
        raise VPNServerDoesNotExist(message=f'VPN Server {vpn_server_name} does not exist')
    # check server response
    try:
        outline_client.get_server_information()
    except Exception as err:
        raise VPNServerDoesNotResponse(message=f'{err!r}')
    else:
        return outline_client

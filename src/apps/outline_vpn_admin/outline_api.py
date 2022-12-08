from outline_vpn.outline_vpn import OutlineVPN
from apps.outline_vpn_admin.models import VPNServer
from apps.outline_vpn_admin.exceptions import VPNServerDoesNotExist, VPNServerDoesNotResponse


def get_outline_client(vpn_server: VPNServer = None) -> OutlineVPN:
    if vpn_server:
        outline_client = OutlineVPN(vpn_server.uri)
    else:
        outline_client = OutlineVPN(VPNServer.objects.get(is_default=True).uri)
    # check server response
    try:
        outline_client.get_server_information()
    except Exception as err:
        raise VPNServerDoesNotResponse(message=f'Сервер {vpn_server.name} не отвечает. {err=!r}')
    else:
        return outline_client

import requests
from outline_vpn.outline_vpn import OutlineVPN
from apps.outline_vpn_admin.models import VPNServer
from apps.outline_vpn_admin.exceptions import VPNServerDoesNotResponse


class MyOutlineVPN(OutlineVPN):
    def get_metrics_transfer(self):
        """
        Метод, для получения использованных байт каждым ключом.
        response = {'bytesTransferredByUserId': {'5': 136931809, '7': 269727691}}
        :return: {'5': 136931809, '7': 269727691}
        """
        response = requests.get(
            f"{self.api_url}/metrics/transfer/", verify=False
        )
        if response.status_code >= 400 or "bytesTransferredByUserId" not in response.json():
            raise Exception("Unable to get metrics")
        return response.json()["bytesTransferredByUserId"]


def get_outline_client(vpn_server: VPNServer = None) -> MyOutlineVPN:
    if vpn_server:
        outline_client = MyOutlineVPN(vpn_server.uri)
    else:
        outline_client = MyOutlineVPN(VPNServer.objects.get(is_default=True).uri)
    # check server response
    try:
        outline_client.get_server_information()
    except Exception as err:
        raise VPNServerDoesNotResponse(message=f'Сервер {vpn_server.name} не отвечает. {err=!r}')
    else:
        return outline_client

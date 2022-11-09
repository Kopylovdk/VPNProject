from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from apps.api.renderers import BaseJSONRenderer
from rest_framework import status
from rest_framework.response import Response
from apps.outline_vpn_admin import exceptions
from apps.outline_vpn_admin.processes import (
    get_tariff,
    create_or_update_contact,
    token_renew,
    get_client_tokens,
    get_client,
    token_new,
    get_vpn_servers,
    get_transports,
    add_traffic_limit,
    del_traffic_limit,
    del_outline_vpn_key,
    telegram_message_sender,
    get_token_info,
)
import logging


log = logging.getLogger(__name__)


class BaseAPIView(views.APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (BaseJSONRenderer,)


class Tariff(BaseAPIView):
    def get(self, request):
        return Response(get_tariff(), status=status.HTTP_200_OK)


class VPNServer(BaseAPIView):
    def get(self, request):
        return Response(get_vpn_servers(), status=status.HTTP_200_OK)


class ContactCreateOrUpdate(BaseAPIView):
    def post(self, request):
        data = request.data
        try:
            response = create_or_update_contact(
                transport_name=data['transport_name'],
                credentials=data['credentials'],
            )
        except exceptions.TransportDoesNotExist as err:
            msg = str(err.message)
            log.error(msg)
            return Response({"details": msg}, status=status.HTTP_404_NOT_FOUND)
        else:
            log.debug(f'{response}')
            if 'Created' in response["details"]:
                return Response(response, status=status.HTTP_201_CREATED)
            return Response(response, status=status.HTTP_200_OK)

    def get(self, request, transport_name, messenger_id):
        try:
            response = get_client(transport_name=transport_name, messenger_id=messenger_id)
        except (
            exceptions.TransportDoesNotExist,
            exceptions.UserDoesNotExist,
        ) as err:
            msg = str(err.message)
            log.error(msg)
            return Response({"details": msg}, status=status.HTTP_404_NOT_FOUND)
        else:
            log.debug(f'{response}')
            return Response(response, status=status.HTTP_200_OK)


class VPNTokenNew(BaseAPIView):
    def post(self, request):
        data = request.data
        try:
            response = token_new(
                transport_name=data['transport_name'],
                credentials=data['credentials'],
                server_name=data['server_name'],
                tariff=data['tariff']
            )
        except exceptions.DemoKeyExist as err:
            msg = str(err.message)
            log.error(msg)
            return Response({"details": msg}, status=status.HTTP_403_FORBIDDEN)
        except (
            exceptions.TransportDoesNotExist,
            exceptions.UserDoesNotExist,
            exceptions.VPNServerDoesNotExist,
            exceptions.TariffDoesNotExist,
        ) as err:
            msg = str(err.message)
            log.error(msg)
            return Response({"details": msg}, status=status.HTTP_404_NOT_FOUND)
        else:
            log.debug(f'{response}')
            return Response(response, status=status.HTTP_201_CREATED)


class VPNTokenRenew(BaseAPIView):
    def post(self, request):
        data = request.data
        log.info(f"{data=!r}")
        try:
            response = token_renew(
                transport_name=data['transport_name'],
                credentials=data['credentials'],
                token_id=data['token_id'],
            )
        except (
            exceptions.TransportDoesNotExist,
            exceptions.UserDoesNotExist,
        ) as err:
            msg = str(err.message)
            log.error(msg)
            return Response({"details": msg}, status=status.HTTP_404_NOT_FOUND)
        except (
            exceptions.BelongToAnotherUser,
            exceptions.DemoKeyExist,
        ) as err:
            msg = str(err.message)
            log.error(msg)
            return Response({"details": msg}, status=status.HTTP_403_FORBIDDEN)
        else:
            log.debug(f'{response}')
            return Response(response, status=status.HTTP_201_CREATED)


class VPNTokens(BaseAPIView):
    def get(self, request, transport_name, messenger_id):
        try:
            response = get_client_tokens(
                transport_name=transport_name,
                messenger_id=messenger_id,
            )
        except (
            exceptions.TransportDoesNotExist,
            exceptions.UserDoesNotExist,
        ) as err:
            msg = str(err.message)
            log.error(msg)
            return Response({"details": msg}, status=status.HTTP_404_NOT_FOUND)
        else:
            log.debug(f'{response}')
            return Response(response, status=status.HTTP_200_OK)


# TODO: Tests needed
class VPNToken(BaseAPIView):
    def get(self, request, token_id):
        try:
            response = get_token_info(token_id)
        except exceptions.VPNTokenDoesNotExist as err:
            msg = str(err.message)
            log.error(msg)
            return Response({'details': msg}, status=status.HTTP_404_NOT_FOUND)
        else:
            log.debug(f'{response}')
            return Response(response, status=status.HTTP_200_OK)

    def patch(self, request):
        data = request.data
        if "limit_in_bytes" in data.keys:
            try:
                response = add_traffic_limit(
                    token_id=data['token_id'],
                    limit_in_bytes=data['limit_in_bytes'],
                )
            except exceptions.VPNServerResponseError as err:
                msg = str(err.message)
                log.error(msg)
                return Response({'details': msg}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except (
                exceptions.VPNServerDoesNotExist,
                exceptions.VPNTokenDoesNotExist,
            ) as err:
                msg = str(err.message)
                log.error(msg)
                return Response({'details': msg}, status=status.HTTP_404_NOT_FOUND)
            else:
                log.debug(f'{response}')
                return Response(response, status=status.HTTP_200_OK)
        else:
            try:
                response = del_traffic_limit(
                    token_id=data['token_id'],
                )
            except exceptions.VPNServerResponseError as err:
                msg = str(err.message)
                log.error(msg)
                return Response({'details': msg}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except (
                exceptions.VPNServerDoesNotExist,
                exceptions.VPNTokenDoesNotExist,
            ) as err:
                msg = str(err.message)
                log.error(msg)
                return Response({'details': msg}, status=status.HTTP_404_NOT_FOUND)
            else:
                log.debug(f'{response}')
                return Response(response, status=status.HTTP_200_OK)

    def delete(self, request):
        try:
            response = del_traffic_limit(request.data['token_id'])
        except exceptions.VPNServerResponseError as err:
            msg = str(err.message)
            log.error(msg)
            return Response({'details': msg}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except (
            exceptions.VPNServerDoesNotExist,
            exceptions.VPNTokenDoesNotExist,
        ) as err:
            msg = str(err.message)
            log.error(msg)
            return Response({'details': msg}, status=status.HTTP_404_NOT_FOUND)
        else:
            log.debug(f'{response}')
            return Response(response, status=status.HTTP_200_OK)


class Transport(BaseAPIView):
    def get(self, request):
        return Response(get_transports(), status=status.HTTP_200_OK)


class TelegramMessageSend(BaseAPIView):
    def post(self, request):
        data = request.data
        try:
            response = telegram_message_sender(
                transport_name=data['transport_name'],
                text=data['text'],
                messenger_id=data['messenger_id'],
            )
        except exceptions.TransportMessageSendError as err:
            msg = str(err.message)
            log.error(msg)
            return Response({'details': msg}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except (
                exceptions.TransportDoesNotExist,
        ) as err:
            msg = str(err.message)
            log.error(msg)
            return Response({"details": msg}, status=status.HTTP_404_NOT_FOUND)
        else:
            log.debug(f'{response}')
            return Response(response, status=status.HTTP_200_OK)


class VPNTokenAdminRenew(BaseAPIView):
    pass


class VPNTokenAdminNew(BaseAPIView):
    pass

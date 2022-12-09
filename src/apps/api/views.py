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
    update_token_valid_until,
    telegram_message_sender,
    get_token_info,
)
from apps.outline_vpn_admin.cashe_update import get_actual_cache_date
import logging


log = logging.getLogger(__name__)


class BaseAPIView(views.APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (BaseJSONRenderer,)


class Tariff(BaseAPIView):
    def get(self, request):
        response = get_tariff()
        response['cache_update_date'] = get_actual_cache_date().isoformat()
        return Response(response, status=status.HTTP_200_OK)


class VPNServer(BaseAPIView):
    def get(self, request):
        response = get_vpn_servers()
        response['cache_update_date'] = get_actual_cache_date().isoformat()
        return Response(response, status=status.HTTP_200_OK)


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
            return Response({"details": f'{msg}'}, status=status.HTTP_404_NOT_FOUND)
        else:
            response['cache_update_date'] = get_actual_cache_date().isoformat()
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
            return Response({"details": f'{msg}'}, status=status.HTTP_404_NOT_FOUND)
        else:
            response['cache_update_date'] = get_actual_cache_date().isoformat()
            log.debug(f'{response}')
            return Response(response, status=status.HTTP_200_OK)


class VPNTokenNew(BaseAPIView):
    def post(self, request):
        data = request.data
        data_keys = data.keys()
        try:
            response = token_new(
                transport_name=data['transport_name'] if 'transport_name' in data_keys else None,
                credentials=data['credentials'] if 'credentials' in data_keys else None,
                server_name=data['server_name'],
                tariff_name=data['tariff_name'],
            )
        except (
            exceptions.DemoKeyExist,
            exceptions.DemoKeyNotAllowed,
        ) as err:
            msg = str(err.message)
            log.error(msg)
            return Response({"details": f'{msg}'}, status=status.HTTP_403_FORBIDDEN)
        except (
            exceptions.TransportDoesNotExist,
            exceptions.UserDoesNotExist,
            exceptions.VPNServerDoesNotExist,
            exceptions.VPNServerDoesNotResponse,
            exceptions.TariffDoesNotExist,
        ) as err:
            msg = str(err.message)
            log.error(msg)
            return Response({"details": f'{msg}'}, status=status.HTTP_404_NOT_FOUND)
        else:
            response['cache_update_date'] = get_actual_cache_date().isoformat()
            log.debug(f'{response}')
            return Response(response, status=status.HTTP_201_CREATED)


class VPNTokenRenew(BaseAPIView):
    def post(self, request):
        data = request.data
        data_keys = data.keys()
        try:
            response = token_renew(
                transport_name=data['transport_name'] if 'transport_name' in data_keys else None,
                credentials=data['credentials'] if 'credentials' in data_keys else None,
                token_id=data['token_id'],
            )
        except (
            exceptions.TransportDoesNotExist,
            exceptions.UserDoesNotExist,
        ) as err:
            msg = str(err.message)
            log.error(msg)
            return Response({"details": f'{msg}'}, status=status.HTTP_404_NOT_FOUND)
        except (
            exceptions.BelongToAnotherUser,
            exceptions.DemoKeyExist,
            exceptions.DemoKeyNotAllowed
        ) as err:
            msg = str(err.message)
            log.error(msg)
            return Response({"details": f'{msg}'}, status=status.HTTP_403_FORBIDDEN)
        else:
            response['cache_update_date'] = get_actual_cache_date().isoformat()
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
            return Response({"details": f'{msg}'}, status=status.HTTP_404_NOT_FOUND)
        else:
            response['cache_update_date'] = get_actual_cache_date().isoformat()
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
            return Response({'details': f'{msg}'}, status=status.HTTP_404_NOT_FOUND)
        else:
            response['cache_update_date'] = get_actual_cache_date().isoformat()
            log.debug(f'{response}')
            return Response(response, status=status.HTTP_200_OK)

    def patch(self, request):
        data = request.data
        data_keys = data.keys()
        if "traffic_limit" in data_keys:
            log.error(f'{data=!r}')
            try:
                response = add_traffic_limit(
                    token_id=data['token_id'],
                    traffic_limit=int(data['traffic_limit']),
                )
            except exceptions.VPNServerResponseError as err:
                msg = str(err.message)
                log.error(msg)
                return Response({'details': f'{msg}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except (
                exceptions.VPNServerDoesNotExist,
                exceptions.VPNServerDoesNotResponse,
                exceptions.VPNTokenDoesNotExist,
            ) as err:
                msg = str(err.message)
                log.error(msg)
                return Response({'details': f'{msg}'}, status=status.HTTP_404_NOT_FOUND)
            else:
                response['cache_update_date'] = get_actual_cache_date().isoformat()
                log.debug(f'{response}')
                return Response(response, status=status.HTTP_200_OK)
        elif "valid_until" in data_keys:
            try:
                response = update_token_valid_until(
                    token_id=data['token_id'],
                    valid_until=int(data['valid_until']),
                )
            except exceptions.VPNTokenDoesNotExist as err:
                msg = str(err.message)
                log.error(msg)
                return Response({'details': f'{msg}'}, status=status.HTTP_404_NOT_FOUND)
            else:
                response['cache_update_date'] = get_actual_cache_date().isoformat()
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
                return Response({'details': f'{msg}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            except (
                exceptions.VPNServerDoesNotExist,
                exceptions.VPNTokenDoesNotExist,
                exceptions.VPNServerDoesNotResponse,
            ) as err:
                msg = str(err.message)
                log.error(msg)
                return Response({'details': f'{msg}'}, status=status.HTTP_404_NOT_FOUND)
            else:
                response['cache_update_date'] = get_actual_cache_date().isoformat()
                log.debug(f'{response}')
                return Response(response, status=status.HTTP_200_OK)

    def delete(self, request):
        try:
            response = del_outline_vpn_key(request.data['token_id'])
        except exceptions.VPNServerResponseError as err:
            msg = str(err.message)
            log.error(msg)
            return Response({'details': f'{msg}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except (
            exceptions.VPNServerDoesNotExist,
            exceptions.VPNServerDoesNotResponse,
            exceptions.VPNTokenDoesNotExist,
        ) as err:
            msg = str(err.message)
            log.error(msg)
            return Response({'details': f'{msg}'}, status=status.HTTP_404_NOT_FOUND)
        else:
            response['cache_update_date'] = get_actual_cache_date().isoformat()
            log.debug(f'{response}')
            return Response(response, status=status.HTTP_200_OK)


class Transport(BaseAPIView):
    def get(self, request):
        response = get_transports()
        response['cache_update_date'] = get_actual_cache_date().isoformat()
        return Response(response, status=status.HTTP_200_OK)


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
            return Response({'details': f'{msg}'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        except (
                exceptions.TransportDoesNotExist,
        ) as err:
            msg = str(err.message)
            log.error(msg)
            return Response({"details": f'{msg}'}, status=status.HTTP_404_NOT_FOUND)
        else:
            response['cache_update_date'] = get_actual_cache_date().isoformat()
            log.debug(f'{response}')
            return Response(response, status=status.HTTP_200_OK)

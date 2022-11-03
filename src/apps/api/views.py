from decimal import Decimal

from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from apps.api.renderers import BaseJSONRenderer
from rest_framework import status
from rest_framework.response import Response
from apps.outline_vpn_admin import exceptions
from apps.outline_vpn_admin.processes import get_tariff, create_or_update_contact, token_new, token_renew, \
    get_client_tokens, get_client, token_demo, get_vpn_servers
import logging


log = logging.getLogger(__name__)


class BaseAPIView(views.APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (BaseJSONRenderer,)

# TODO: тесты


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
            return Response({"details": str(err.message)}, status=status.HTTP_404_NOT_FOUND)
        else:
            if 'created' in response["details"]:
                return Response(response, status=status.HTTP_201_CREATED)
            return Response(response, status=status.HTTP_200_OK)

    def get(self, request, transport_name, messenger_id):
        try:
            return Response(
                get_client(
                    transport_name=transport_name,
                    messenger_id=messenger_id
                ),
                status=status.HTTP_200_OK
            )
        except (exceptions.TransportDoesNotExist, exceptions.UserDoesNotExist) as err:
            return Response({"details": str(err.message)}, status=status.HTTP_404_NOT_FOUND)


class VPNTokenNew(BaseAPIView):
    def post(self, request):
        data = request.data
        try:
            response = token_new(
                transport_name=data['transport_name'],
                credentials=data['credentials'],
                server_name=data['server_name'],
            )
        except (
            exceptions.TransportDoesNotExist,
            exceptions.UserDoesNotExist,
            exceptions.VPNServerDoesNotExist
        ) as err:
            return Response({"details": str(err.message)}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(response, status=status.HTTP_201_CREATED)


class VPNTokenRenew(BaseAPIView):
    def post(self, request):
        data = request.data
        log.info(f"{data=!r}")
        try:
            response = token_renew(
                transport_name=data['transport_name'],
                credentials=data['credentials'],
                token_id=data['outline_id'],
            )
        except (
            exceptions.TransportDoesNotExist,
            exceptions.UserDoesNotExist,
        ) as err:
            log.error('DoesNotExist')
            return Response({"details": str(err.message)}, status=status.HTTP_404_NOT_FOUND)
        except exceptions.BelongToAnotherUser as err:
            log.error('BelongToAnotherUser')
            return Response({"details": str(err.message)}, status=status.HTTP_403_FORBIDDEN)
        else:
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
            return Response({"details": str(err.message)}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(response, status=status.HTTP_200_OK)


class VPNTokenDemo(BaseAPIView):
    def post(self, request):
        data = request.data
        try:
            response = token_demo(
                transport_name=data['transport_name'],
                credentials=data['credentials'],
                server_name=data['server_name'],
            )
        except exceptions.DemoKeyExist as err:
            return Response({"details": str(err.message)}, status=status.HTTP_403_FORBIDDEN)
        except (
                exceptions.TransportDoesNotExist,
                exceptions.UserDoesNotExist,
                exceptions.VPNServerDoesNotExist
        ) as err:
            return Response({"details": str(err.message)}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(response, status=status.HTTP_201_CREATED)

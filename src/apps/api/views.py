from rest_framework import views
from rest_framework.permissions import IsAuthenticated
from apps.api.renderers import BaseJSONRenderer
from rest_framework import status
from rest_framework.response import Response
from apps.outline_vpn_admin.processes import get_tariff, create_or_update_contact, token_new, token_renew, \
    get_client_tokens, get_client, token_demo, get_vpn_servers
import logging
log = logging.getLogger(__name__)


class BaseAPIView(views.APIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (BaseJSONRenderer,)

# TODO: Обработка исключений, тесты


class Tariff(BaseAPIView):
    def get(self, request):
        return Response(get_tariff(), status=status.HTTP_200_OK)


class VPNServer(BaseAPIView):
    def get(self, request):
        return Response(get_vpn_servers(), status=status.HTTP_200_OK)


class ContactCreateOrUpdate(BaseAPIView):
    def post(self, request):
        data = request.data

        response = create_or_update_contact(
            transport_name=data['transport_name'],
            credentials=data['credentials'],
        )
        if 'created' in response["details"]:
            return Response(response, status=status.HTTP_201_CREATED)
        return Response(response, status=status.HTTP_200_OK)

    def get(self, request, transport_name, messenger_id):
        return Response(
            get_client(
                transport_name=transport_name,
                messenger_id=messenger_id
            ),
            status=status.HTTP_200_OK
        )


class VPNToken(BaseAPIView):
    def post(self, request, token_id=None):
        data = request.data
        if token_id:
            response = token_renew(
                transport_name=data['transport_name'],
                credentials=data['credentials'],
                server_name=data['server_name'],
                token_id=token_id,
            )
        else:
            response = token_new(
                transport_name=data['transport_name'],
                credentials=data['credentials'],
                server_name=data['server_name'],
            )
        return Response(response, status=status.HTTP_201_CREATED)

    def get(self, request, transport_name, messenger_id):
        return Response(
            get_client_tokens(
                transport_name=transport_name,
                messenger_id=messenger_id,
            ),
            status=status.HTTP_200_OK
        )


class VPNTokenDemo(BaseAPIView):
    def post(self, request):
        data = request.data
        response = token_demo(
            transport_name=data['transport_name'],
            credentials=data['credentials'],
            server_name=data['server_name'],
        )
        return Response(response, status=status.HTTP_201_CREATED)

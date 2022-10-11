# from rest_framework import views
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.generics import get_object_or_404
# from rest_framework.permissions import IsAuthenticated
# from apps.api.renderers import BaseJSONRenderer
# from apps.api.serializers import TelegramUsersSerializer, OutlineVPNKeysSerializer
# from apps.outline_vpn_admin.models import TelegramUsers, OutlineVPNKeys
# from rest_framework import status
# from rest_framework.response import Response
# from apps.outline_vpn_admin.processes import add_new_tg_user, create_new_key, add_traffic_limit
# import logging
# log = logging.getLogger(__name__)
#
#
# def response_unknown_command(command: str) -> Response:
#     return Response({'detail': f'Unknown command {command!r}'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#
#
# class BaseModelView(views.APIView):
#     permission_classes = (IsAuthenticated,)
#     renderer_classes = (BaseJSONRenderer,)
#
#
# class TelegramUsersModelView(BaseModelView):
#     allow_post_commands = [
#         'create_or_update_user',
#     ]
#     serializer_class = TelegramUsersSerializer
#
#     def get(self, request, tg_id=None):
#         tg_user = get_object_or_404(TelegramUsers, telegram_id=tg_id)
#         serializer = self.serializer_class(tg_user)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def post(self, request):
#         command = request.data['command']
#         if command in self.allow_post_commands:
#             if command == 'create_or_update_user':
#                 tg_user = request.data.get('tg_user')
#                 serializer = self.serializer_class(data=tg_user)
#                 serializer.is_valid(raise_exception=True)
#                 add_new_tg_user(tg_user)
#                 return Response({'create_or_update_user': status.HTTP_200_OK}, status=status.HTTP_200_OK)
#             else:
#                 return response_unknown_command(command)
#         else:
#             return response_unknown_command(command)
#
#
# class OutlineVPNKeysModelView(BaseModelView):
#     allow_post_commands = [
#         'create_demo_token',
#         'create_new_token',
#         'refresh_token',
#     ]
#     allow_patch_commands = [
#         'add_user_to_token',
#         'token_valid_date',
#         'token_is_active',
#         'token_name',
#         'token_traffic_limit',
#     ]
#     allow_delete_commands = [
#         'token_delete',
#     ]
#     serializer_class = OutlineVPNKeysSerializer
#
#     def post(self, request, tg_id=None, vpn_key_id=None, srv_name=None):
#         command = request.data['command']
#         if command in self.allow_post_commands:
#             if command == 'new_key':
#                 api_server_name = request.data.get(srv_name)
#                 api_key = create_new_key(api_server_name)
#                 serializer = self.serializer_class(api_key)
#                 return Response({'vpn_keys': serializer.data}, status=status.HTTP_201_CREATED)
#             elif command == 'demo_key':
#                 api_server_name = request.data.get(srv_name)
#                 api_demo_key = create_new_key(api_server_name)
#                 api_demo_key.add_tg_user(tg_id)
#                 api_demo_key.change_active_status()
#                 api_demo_key.change_valid_until(7)
#                 add_traffic_limit(srv_name, api_demo_key, 1024 * 1024 * 1024)
#                 serializer = self.serializer_class(api_demo_key)
#                 return Response({'vpn_keys': serializer.data}, status=status.HTTP_201_CREATED)
#             else:
#                 return response_unknown_command(command)
#         else:
#             return response_unknown_command(command)
#
#     # def get(self, request):
#     #     pass
from django.urls import path
import apps.api.views as api_views
from rest_framework.authtoken import views
from django.views.decorators.csrf import csrf_exempt
app_name = 'api'

urlpatterns = [
    # get
    path('actual-cache-date/', api_views.GetActualCacheDate.as_view(), name='get_actual_cache_date'),
    path('tariff/', api_views.Tariff.as_view(), name='get_tariffs'),
    path('vpn-servers/', api_views.VPNServer.as_view(), name='get_vpn_servers'),
    path('transports/', api_views.Transport.as_view(), name='get_transports'),
    path('contact/<str:transport_name>/<int:messenger_id>', api_views.ContactCreateOrUpdate.as_view(), name='get_cont'),
    path('token/<str:transport_name>/<int:messenger_id>', api_views.VPNTokens.as_view(), name='get_client_tokens'),
    path('token/<int:token_id>', api_views.VPNToken.as_view(), name='get_token_info'),

    # post
    path('api-token-auth/', csrf_exempt(views.obtain_auth_token), name='get_auth_token'),
    path('contact/', api_views.ContactCreateOrUpdate.as_view(), name='creat_or_update_contact'),
    path('token/renew/', api_views.VPNTokenRenew.as_view(), name='renew_exist_token'),
    path('token/new/', api_views.VPNTokenNew.as_view(), name='create_new_token'),
    path('message/telegram/send/', api_views.TelegramMessageSend.as_view(), name='telegram_message_send'),

    # patch
    path('token/', api_views.VPNToken.as_view(), name='update_token'),

    # delete
    path('token/delete/', api_views.VPNToken.as_view(), name='delete_token'),
]

from django.urls import path
import apps.api.views as api_views
from rest_framework.authtoken import views
app_name = 'api'

urlpatterns = [
    path('api-token-auth/', views.obtain_auth_token, name='get_auth_token'),
    # get
    path('tariff/', api_views.Tariff.as_view(), name='get_tariffs'),
    path('contact/<str:transport_name>/<int:messenger_id>', api_views.ContactCreateOrUpdate.as_view(), name='get_cont'),
    path('token/<str:transport_name>/<int:messenger_id>', api_views.VPNTokens.as_view(), name='get_client_tokens'),
    path('vpn-servers/', api_views.VPNServer.as_view(), name='get_vpn_servers'),

    # post
    path('contact/', api_views.ContactCreateOrUpdate.as_view(), name='creat_or_update_contact'),
    path('token/renew/', api_views.VPNTokenRenew.as_view(), name='renew_exist_token'),
    path('token/new/', api_views.VPNTokenNew.as_view(), name='create_new_token'),

    # patch
    # path('vpn_token/<int:vpn_key_id>/user/<int:tg_id>/<str:srv_name>/', api_views.OutlineVPNKeysModelView.as_view()),
    # path('vpn_token/<int:vpn_key_id>/<str:srv_name>/', api_views.OutlineVPNKeysModelView.as_view()),
]

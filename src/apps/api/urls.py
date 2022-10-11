# from django.urls import path
# import apps.api.views as api_views
# from rest_framework.authtoken import views
# app_name = 'api'
#
# urlpatterns = [
#     path('api-token-auth/', views.obtain_auth_token),
#
#     # get
#     path('user/<int:tg_id>/', api_views.TelegramUsersModelView.as_view(), name='get_user'),
#     path('user/<int:tg_id>/vpn_keys/<str:srv_name>/', api_views.OutlineVPNKeysModelView.as_view()),
#
#     # post
#     path('user/', api_views.TelegramUsersModelView.as_view()),
#     path('vpn_token/<int:tg_id>/<str:srv_name>/', api_views.OutlineVPNKeysModelView.as_view()),
#     path('vpn_token/<int:vpn_key_id>/refresh/<str:srv_name>/', api_views.OutlineVPNKeysModelView.as_view()),
#     path('vpn_token/<str:srv_name>/', api_views.OutlineVPNKeysModelView.as_view()),
#
#     # patch
#     path('vpn_token/<int:vpn_key_id>/user/<int:tg_id>/<str:srv_name>/', api_views.OutlineVPNKeysModelView.as_view()),
#     path('vpn_token/<int:vpn_key_id>/<str:srv_name>/', api_views.OutlineVPNKeysModelView.as_view()),
# ]
#
#

import logging
from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
from django.utils.translation import ngettext
from django.contrib import messages
# from rest_framework.authtoken.models import Token

from apps.outline_vpn_admin.models import TelegramUsers, OutlineVPNKeys
from apps.outline_vpn_admin.processes import (
    create_new_key,
    add_traffic_limit,
    del_traffic_limit,
    del_outline_vpn_key,
)


log = logging.getLogger(__name__)


# @admin.register(Token)
# class BotsTokens(admin.ModelAdmin):
#     pass


@admin.register(TelegramUsers)
class VPNServiceTelegramUsersAdmin(admin.ModelAdmin):
    list_display = (
        'telegram_id',
        'telegram_login',
        'telegram_first_name',
        'telegram_last_name',
        'is_admin',
        'created_at',
    )

    search_fields = (
        'telegram_login',
        'telegram_first_name',
        'telegram_last_name',
    )

    list_filter = (
        'telegram_id',
        'telegram_login',
        'is_admin',
    )
    actions = ['change_admin_status']

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    @admin.action(description='Change admin role')
    def change_admin_status(self, request, queryset):
        for obj in queryset:
            obj.change_is_admin()
        objects = len(queryset)
        self.message_user(request, ngettext(
            '%d role was successfully changed.',
            '%d roles were successfully changed.',
            objects,
        ) % objects, messages.SUCCESS)


@admin.register(OutlineVPNKeys)
class VPNServiceOutlineVPNKeysAdmin(admin.ModelAdmin):
    change_list_template = 'change_list.html'

    list_display = (
        'telegram_user_record',
        'outline_key_id',
        'outline_key_name',
        'outline_key_valid_until',
        'outline_key_traffic_limit',
        'outline_key_active',
        'created_at',
    )

    search_fields = (
        'outline_key_name',
    )

    list_filter = (
        'telegram_user_record',
        'outline_key_active',
        'outline_key_valid_until',
    )

    actions = [
        'change_vpn_status',
        'del_traffic_limit',
        'add_default_traffic_limit',
        'delete_vpn_record',
    ]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('add_new_vpn_key/', self.add_new_vpn_key)
        ]
        return my_urls + urls

    def add_new_vpn_key(self, request):
        vpn_key = create_new_key('kz')
        add_traffic_limit('kz', vpn_key)
        self.message_user(request, "New VPN Key Added with limit 1 kb")
        return HttpResponseRedirect("../")

    @admin.action(description='Delete VPN record')
    def delete_vpn_record(self, request, queryset):
        objects = len(queryset)
        for obj in queryset:
            del_outline_vpn_key('kz', obj)

        self.message_user(request, ngettext(
            '%d VPN record was successfully deleted.',
            '%d VPN records were successfully deleted.',
            objects,
        ) % objects, messages.SUCCESS)

    @admin.action(description='Change VPN status')
    def change_vpn_status(self, request, queryset):
        for obj in queryset:
            obj.change_active_status()

        objects = len(queryset)
        self.message_user(request, ngettext(
            '%d VPN status was successfully changed.',
            '%d VPN statuses were successfully changed.',
            objects,
        ) % objects, messages.SUCCESS)

    @admin.action(description='Delete traffic limit')
    def del_traffic_limit(self, request, queryset):
        for obj in queryset:
            del_traffic_limit('kz', obj)

        objects = len(queryset)
        self.message_user(request, ngettext(
            '%d traffic limit was successfully deleted.',
            '%d traffic limits were successfully deleted.',
            objects,
        ) % objects, messages.SUCCESS)

    @admin.action(description='Add default traffic limit')
    def add_default_traffic_limit(self, request, queryset):
        for obj in queryset:
            add_traffic_limit('kz', obj)

        objects = len(queryset)
        self.message_user(request, ngettext(
            '%d default traffic limit was successfully added.',
            '%d default traffic limits were successfully added.',
            objects,
        ) % objects, messages.SUCCESS)

    def response_post_save_change(self, request, obj):
        if not obj.outline_key_traffic_limit:
            del_traffic_limit('kz', obj)
        else:
            add_traffic_limit('kz', obj, obj.outline_key_traffic_limit)

        return super().response_post_save_change(request, obj)

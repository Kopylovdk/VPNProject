import logging
from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import ngettext
from django.contrib import messages
from apps.outline_vpn_admin import models as vpn_models
from apps.outline_vpn_admin import exceptions
from apps.outline_vpn_admin import processes as processes
from apps.outline_vpn_admin.forms import VPNTokenAdminCreateForm, VPNTokenAdminChangeForm
from django.conf.locale.es import formats as es_formats

es_formats.DATETIME_FORMAT = "d M Y"

log = logging.getLogger(__name__)


admin.AdminSite.site_header = 'Tematika administration'
admin.AdminSite.site_title = 'Tematika VPN Admin'
# admin.AdminSite.site_url
admin.site.unregister(Group)
admin.ModelAdmin.save_on_top = True


@admin.register(vpn_models.Currency)
class Currency(admin.ModelAdmin):
    list_display = (
        'name',
        'name_iso',
        'is_main',
        'exchange_rate',
        'is_active',
    )
    search_fields = (
        'name',
    )


@admin.register(vpn_models.VPNServer)
class VPNServer(admin.ModelAdmin):
    list_display = (
        'name',
        'uri',
        'is_default',
        'is_active',
        'created_at',
        'updated_at',
    )

    search_fields = (
        'name',
    )

    list_filter = (
        'name',
    )


@admin.register(vpn_models.Tariff)
class Tariff(admin.ModelAdmin):
    list_display = (
        'name',
        'is_demo',
        'prolong_period',
        'traffic_limit',
        'price',
        'currency',
        'is_active',
    )

    search_fields = (
        'name',
    )

    list_filter = (
        'prolong_period',
        'price',
        'is_active',
        'is_demo',
    )


@admin.register(vpn_models.Transport)
class Transport(admin.ModelAdmin):
    list_display = (
        'name',
        'uid_format',
        'full_name_format',
    )

    search_fields = (
        'name',
    )


@admin.register(vpn_models.Client)
class Client(admin.ModelAdmin):
    list_display = (
        'full_name',
    )

    search_fields = (
        'full_name',
    )


@admin.register(vpn_models.Contact)
class Contact(admin.ModelAdmin):
    list_display = (
        'client',
        'transport',
        'name',
        'phone_number',
    )

    search_fields = (
        'name',
        'phone_number',
    )

    list_filter = (
        'transport',
    )


@admin.register(vpn_models.VPNToken)
class VPNToken(admin.ModelAdmin):
    list_display = (
        'name',
        'outline_id',
        'valid_until',
        'traffic_limit',
        'server',
        'is_demo',
        'is_tech',
        'is_active',
    )

    search_fields = (
        'name',
    )

    list_filter = (
        'server',
        'valid_until',
        'is_active',
        'is_demo',
        'is_tech',
    )

    actions = [
        'change_vpn_status',
        'del_traffic_limit',
        'add_default_traffic_limit',
        'delete_vpn_record',
    ]

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        return super().add_view(request, form_url, extra_context=extra_context)

    def get_form(self, request, obj=None, change=True, **kwargs):
        if 'add' in request.META.get('PATH_INFO'):
            return VPNTokenAdminCreateForm
        else:
            form = VPNTokenAdminChangeForm
            form.base_fields['name'].widget.attrs['style'] = 'width: 30em;'
            return form

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description='Delete VPN record')
    def delete_vpn_record(self, request, queryset):
        objects_qnt = len(queryset)
        for obj in queryset:
            try:
                processes.del_outline_vpn_key(obj.id)
            except exceptions.VPNServerResponseError:
                processes.change_vpn_token_active_state(obj)

        self.message_user(request, ngettext(
            '%d VPN token was successfully deleted.',
            '%d VPN tokens were successfully deleted.',
            objects_qnt,
        ) % objects_qnt, messages.SUCCESS)

    @admin.action(description='Delete traffic limit')
    def del_traffic_limit(self, request, queryset):
        for obj in queryset:
            try:
                processes.del_traffic_limit(obj.id)
            except exceptions.VPNServerResponseError:
                processes.change_vpn_token_traffic_limit(obj)

        objects = len(queryset)
        self.message_user(request, ngettext(
            '%d traffic limit was successfully deleted.',
            '%d traffic limits were successfully deleted.',
            objects,
        ) % objects, messages.SUCCESS)

    @admin.action(description='Add default traffic limit')
    def add_default_traffic_limit(self, request, queryset):
        for obj in queryset:
            try:
                processes.add_traffic_limit(obj.id)
            except exceptions.VPNServerResponseError:
                processes.change_vpn_token_traffic_limit(obj, 1024)

        objects = len(queryset)
        self.message_user(request, ngettext(
            '%d default traffic limit was successfully added.',
            '%d default traffic limits were successfully added.',
            objects,
        ) % objects, messages.SUCCESS)

    def save_model(self, request, obj, form, change):
        if change:
            if not obj.traffic_limit:
                try:
                    processes.del_traffic_limit(obj.id)
                except exceptions.VPNServerResponseError:
                    processes.change_vpn_token_traffic_limit(obj)
            else:
                try:
                    processes.add_traffic_limit(obj.id, obj.traffic_limit)
                except exceptions.VPNServerResponseError:
                    processes.change_vpn_token_traffic_limit(obj, obj.traffic_limit)
        else:
            processes.token_new(
                server_name=obj.server.name,
                tariff_name=obj.tariff.name,
            )


@admin.register(vpn_models.TokenProcess)
class TokenProcess(admin.ModelAdmin):
    list_display = (
        'script_name',
        'created_at',
        'is_executed',
        'executed_at',
    )

    search_fields = (
        'script_name',
    )

    list_filter = (
        'script_name',
        'vpn_token',
        'vpn_server',
        'is_executed',
    )

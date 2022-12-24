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
admin.site.unregister(Group)
admin.ModelAdmin.save_on_top = True


def format_bytes_to_human(size: int) -> str:
    info_size = 1024
    n = 0
    info_labels = ['байт', 'Кб', 'Мб', 'Гб', 'Тб', 'Пб', 'Эб', 'Зб', 'Йб']
    while size >= info_size:
        size /= info_size
        n += 1
    return f"{size:.2f} {info_labels[n]}"


class BaseNoDeleteModelAdmin(admin.ModelAdmin):
    model_name = ''
    actions = [
        'change_active_status',
    ]

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description='Change active status')
    def change_active_status(self, request, queryset):
        for obj in queryset:
            obj.is_active = False if obj.is_active else True
            obj.save()
        cnt = queryset.count()
        self.message_user(request, ngettext(
            f'%d {self.model_name} activity was successfully changed.',
            f'%d {self.model_name}s activity was successfully changed.',
            cnt,
        ) % cnt, messages.SUCCESS)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        return super().add_view(request, form_url, extra_context=extra_context)


@admin.register(vpn_models.Currency)
class Currency(BaseNoDeleteModelAdmin):
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

    model_name = 'Currency'


@admin.register(vpn_models.VPNServer)
class VPNServer(BaseNoDeleteModelAdmin):
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
    model_name = 'VPNServer'


@admin.register(vpn_models.Tariff)
class Tariff(BaseNoDeleteModelAdmin):
    list_display = (
        'name',
        'is_demo',
        'prolong_period',
        'traffic_limit_',
        'price',
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

    model_name = "Tariff"

    @admin.display(description='Лимит')
    def traffic_limit_(self, obj):
        traffic_limit = obj.traffic_limit
        if traffic_limit:
            return format_bytes_to_human(traffic_limit)
        return ''


@admin.register(vpn_models.Transport)
class Transport(BaseNoDeleteModelAdmin):
    list_display = (
        'name',
        'uid_format',
        'full_name_format',
        'is_active',
        'is_admin_transport',
    )

    search_fields = (
        'name',
    )
    model_name = 'Transport'


@admin.register(vpn_models.Client)
class Client(admin.ModelAdmin):
    list_display = (
        'id',
        'full_name',
        'vpn_tokens_cnt',
        'contacts_cnt',
    )

    search_fields = (
        'full_name',
    )

    @admin.display(description='Всего ключей')
    def vpn_tokens_cnt(self, obj):
        return obj.vpntoken_set.count()

    @admin.display(description='Всего контактов')
    def contacts_cnt(self, obj):
        return obj.contact_set.count()


@admin.register(vpn_models.Contact)
class Contact(admin.ModelAdmin):
    list_display = (
        'client',
        'transport',
        'uid',
        'phone_number',
    )

    search_fields = (
        'client__full_name',
        'phone_number',
    )

    list_filter = (
        'transport',
    )


@admin.register(vpn_models.VPNToken)
class VPNToken(admin.ModelAdmin):
    default_traffic_limit = 1024 * 1024 * 1024
    list_display = (
        'name',
        'outline_id',
        'valid_until',
        'traffic_limit_',
        'server',
        'is_demo',
        'is_tech',
        'is_active',
        'client',
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

    @admin.display(description='Лимит')
    def traffic_limit_(self, obj):
        traffic_limit = obj.traffic_limit
        if traffic_limit:
            return format_bytes_to_human(traffic_limit)
        return ''

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        return super().add_view(request, form_url, extra_context=extra_context)

    def get_form(self, request, obj=None, change=True, **kwargs):
        if 'add' in request.META.get('PATH_INFO'):
            return VPNTokenAdminCreateForm
        else:
            form = super().get_form(request, obj, change, **kwargs)
            # not_editable_fields = [
            #     'outline_id',
            #     'previous_vpn_token_id',
            #     'vpn_key',
            #     'is_demo',
            #     'is_tech',
            #     'is_active',
            # ]
            # for field_name, field in form.base_fields.items():
            #     if field_name in not_editable_fields:
            #         field.disabled = True
            # form = VPNTokenAdminChangeForm
            form.base_fields['name'].widget.attrs['style'] = 'width: 30em;'
            # form.base_fields['traffic_limit'].help_text = 'Указывайте новое значение в Мб.' \
            #                                               'При сохранении система автоматически пересчитывает в байты.'
            return form

    def has_delete_permission(self, request, obj=None):
        return False

    @admin.action(description='Delete VPN record')
    def delete_vpn_record(self, request, queryset):
        for obj in queryset:
            try:
                processes.del_outline_vpn_key(obj.id)
            except exceptions.VPNServerResponseError:
                processes.change_vpn_token_active_state(obj)
        qnt = queryset.count()
        self.message_user(request, ngettext(
            '%d VPN token was successfully deleted from VPN server.',
            '%d VPN tokens were successfully deleted from VPN server.',
            qnt,
        ) % qnt, messages.SUCCESS)

    @admin.action(description='Delete traffic limit')
    def del_traffic_limit(self, request, queryset):
        for obj in queryset:
            try:
                processes.del_traffic_limit(obj.id)
            except exceptions.VPNServerResponseError:
                processes.change_vpn_token_traffic_limit(obj)

        cnt = queryset.count()
        self.message_user(request, ngettext(
            '%d traffic limit was successfully deleted.',
            '%d traffic limits were successfully deleted.',
            cnt,
        ) % cnt, messages.SUCCESS)

    @admin.action(description='Add default traffic limit')
    def add_default_traffic_limit(self, request, queryset):
        for obj in queryset:
            try:

                processes.add_traffic_limit(obj.id, self.default_traffic_limit)
            except exceptions.VPNServerResponseError:
                processes.change_vpn_token_traffic_limit(obj, self.default_traffic_limit)

        cnt = queryset.count()
        self.message_user(request, ngettext(
            '%d default traffic limit was successfully added.',
            '%d default traffic limits were successfully added.',
            cnt,
        ) % cnt, messages.SUCCESS)

    def save_model(self, request, obj, form, change):
        if change:
            if not obj.traffic_limit:
                try:
                    processes.del_traffic_limit(obj.id)
                except exceptions.VPNServerResponseError:
                    processes.change_vpn_token_traffic_limit(obj, 0)
            else:
                try:
                    processes.add_traffic_limit(obj.id, obj.traffic_limit)
                except exceptions.VPNServerResponseError:
                    processes.change_vpn_token_traffic_limit(obj, obj.traffic_limit)
            super().save_model(request, obj, form, change)
        else:
            processes.token_new(
                client=obj.client,
                server_name=obj.server.name,
                tariff_name=obj.tariff.name,
            )


@admin.register(vpn_models.TokenProcess)
class TokenProcess(admin.ModelAdmin):
    list_display = (
        'script_name',
        'created_at',
        'vpn_token_name',
        'contact',
        'is_executed',
        'executed_at',
    )

    @admin.display(description='Имя VPN ключа')
    def vpn_token_name(self, obj):
        return obj.vpn_token.name

    search_fields = (
        'script_name',
        'contact__client__full_name',
        'vpn_token__name',
    )

    list_filter = (
        'script_name',
        'vpn_server',
        'transport',
        'is_executed',
    )

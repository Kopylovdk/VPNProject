from django import forms
from apps.outline_vpn_admin.exceptions import VPNServerDoesNotResponse
from apps.outline_vpn_admin.models import VPNToken
from apps.outline_vpn_admin.outline_api import get_outline_client


class VPNTokenAdminCreateForm(forms.ModelForm):
    class Meta:
        model = VPNToken
        fields = [
            'server',
            'tariff',
        ]

    def clean(self):
        keys = self.cleaned_data.keys()
        if not self.cleaned_data:
            raise forms.ValidationError("Заполните все поля")
        elif 'tariff' not in keys:
            raise forms.ValidationError("Выберите ТАРИФ")
        elif 'server' not in keys:
            raise forms.ValidationError("Выберите Сервер")
        if self.cleaned_data['tariff'].is_demo:
            raise forms.ValidationError("Создание VPN Token с тарифом DEMO из админки не возможно")
        try:
            get_outline_client(self.cleaned_data['server'])
        except VPNServerDoesNotResponse:
            raise forms.ValidationError("Ошибка подключения к VPN серверу. "
                                        "Обратитесь к администратору и попробуйте позже")


class VPNTokenAdminChangeForm(forms.ModelForm):
    not_editable_fields = [
        'outline_id',
        'previous_vpn_token_id',
        'vpn_key',
        'is_demo',
        'is_tech',
        'is_active',
    ]

    class Meta:
        model = VPNToken
        fields = [
            'client',
            'server',
            'tariff',
            'name',
            'valid_until',
            'traffic_limit',
            'outline_id',
            'previous_vpn_token_id',
            'vpn_key',
            'is_active',
            'is_demo',
            'is_tech',
        ]

    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in self.not_editable_fields:
                field.disabled = True
            if field_name == 'traffic_limit':
                field.help_text = 'Указывайте новое значение в Мб.' \
                                  'При сохранении система автоматически пересчитывает в байты.'

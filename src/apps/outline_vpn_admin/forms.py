from django import forms
from apps.outline_vpn_admin.models import VPNToken


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


class VPNTokenAdminChangeForm(forms.ModelForm):
    not_editable_fields = [
        'outline_id',
        'previous_vpn_token_id',
        'vpn_key',
        'is_demo',
        'is_tech',
        'is_active',
        'created_at',
        'updated_at',
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
            'created_at',
            'updated_at',
        ]

    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        for field_name, field in self.fields.items():
            if field_name in self.not_editable_fields:
                field.disabled = True

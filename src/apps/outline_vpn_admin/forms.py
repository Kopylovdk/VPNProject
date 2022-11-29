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
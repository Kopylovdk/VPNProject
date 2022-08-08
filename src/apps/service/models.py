from django.db import models


class VPNServiceRecord(models.Model):
    class Meta:
        db_table = 'VPNServiceRecord'

    telegram_id = models.IntegerField(verbose_name='ID телеграм', null=True)
    telegram_login = models.CharField(verbose_name='Логин телеграм', max_length=254, null=True, blank=True)
    telegram_first_name = models.CharField(verbose_name='Имя телеграм', max_length=254, null=True, blank=True)
    telegram_last_name = models.CharField(verbose_name='Фамилия телеграм', max_length=254, null=True, blank=True)

    outline_key_id = models.IntegerField(verbose_name='ID OutLine VPN Key', null=True, blank=True)
    outline_key_created_at = models.DateField(verbose_name='Дата добавления ключа VPN', auto_now_add=True)
    outline_key_valid_until = models.DateField(verbose_name='Дата окончания подписки', null=True, blank=True)
    outline_key_active = models.BooleanField(verbose_name='Активность VPN ключа', default=True, null=True, blank=True)

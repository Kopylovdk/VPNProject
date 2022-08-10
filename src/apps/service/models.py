from django.db import models


class TelegramUsers(models.Model):
    class Meta:
        db_table = 'TelegramUsers'
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'
        constraints = [models.UniqueConstraint(fields=['telegram_id'], name='unique_telegram_id')]

    telegram_id = models.IntegerField(verbose_name='ID пользователя телеграм', null=True)
    telegram_login = models.CharField(verbose_name='Логин телеграм', max_length=254, null=True, blank=True)
    telegram_first_name = models.CharField(verbose_name='Имя телеграм', max_length=254, null=True, blank=True)
    telegram_last_name = models.CharField(verbose_name='Фамилия телеграм', max_length=254, null=True, blank=True)

    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)

    def __str__(self):
        return f'{self.telegram_login}_{self.telegram_id}'


class OutlineVPNKeys(models.Model):
    class Meta:
        db_table = 'OutlineVPNKeys'
        verbose_name = 'Outline VPN Key'
        verbose_name_plural = 'Outline VPN Keys'

    telegram_user_record = models.ForeignKey(TelegramUsers, on_delete=models.CASCADE, verbose_name='Владелец ключа')
    outline_key_id = models.IntegerField(verbose_name='ID OutLine VPN Key', null=True, blank=True)
    outline_key_name = models.CharField(
        verbose_name='Имя VPN ключа', max_length=254, null=True, blank=True, default='Отсутствует'
    )
    outline_key_valid_until = models.DateField(verbose_name='Дата окончания подписки', null=True, blank=True)
    outline_key_active = models.BooleanField(verbose_name='Активность VPN ключа', default=True, null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)

    def __str__(self):
        return f'{self.telegram_user_record}_{self.outline_key_name}'

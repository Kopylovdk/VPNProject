from datetime import datetime, timedelta

from django.db import models

from apps.service.outline.outline_api import add_traffic_limit, del_traffic_limit


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
    is_admin = models.BooleanField(verbose_name='Администратор', default=False)

    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)

    def __str__(self):
        return f'{self.telegram_login!r}_{self.telegram_id!r}'


class OutlineVPNKeys(models.Model):
    class Meta:
        db_table = 'OutlineVPNKeys'
        verbose_name = 'Outline VPN Key'
        verbose_name_plural = 'Outline VPN Keys'
        constraints = [
            models.UniqueConstraint(
                fields=['telegram_user_record', 'outline_key_id'],
                name='unique_telegram_user_record_outline_key_id'
            )
        ]

    telegram_user_record = models.ForeignKey(
        TelegramUsers, on_delete=models.CASCADE, verbose_name='Владелец ключа', null=True, blank=True
    )
    outline_key_id = models.IntegerField(verbose_name='ID OutLine VPN Key', null=True, blank=True)
    outline_key_name = models.CharField(
        verbose_name='Имя VPN ключа', max_length=254, null=True, blank=True, default='Отсутствует'
    )
    outline_key_value = models.CharField(verbose_name='VPN ключ', max_length=254, null=True, blank=True)
    outline_key_valid_until = models.DateField(verbose_name='Дата окончания подписки', null=True, blank=True)
    outline_key_active = models.BooleanField(verbose_name='Активность VPN ключа', default=False)
    outline_key_traffic_limit = models.IntegerField(verbose_name='Лимит трафика', null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)

    def __str__(self):
        return f'{self.telegram_user_record!r}_{self.outline_key_name!r}'

    def add_traffic_limit(self, limit_in_bytes: int = 1024) -> None:
        add_traffic_limit(self.outline_key_id, limit_in_bytes)
        self.outline_key_traffic_limit = limit_in_bytes
        self.save()

    def del_traffic_limit(self) -> None:
        del_traffic_limit(self.outline_key_id)
        self.outline_key_traffic_limit = None
        self.save()

    def add_tg_user(self, telegram_user: TelegramUsers) -> None:
        self.telegram_user_record = telegram_user
        self.save()

    def change_active_status(self) -> bool:
        if self.outline_key_active:
            self.outline_key_active = False
        else:
            self.outline_key_active = True
        self.save()
        return self.outline_key_active

    def change_valid_until(self, days: int) -> datetime or None:
        """
        Функция изменения срока действия записи OutlineVPNKeys
        Params:
             days: int
        Returns:
            datetime.datetime
        Exceptions: None
        """
        if not days:
            self.outline_key_valid_until = None
        else:
            self.outline_key_valid_until = datetime.today() + timedelta(days=days)
        self.save()
        return self.outline_key_valid_until

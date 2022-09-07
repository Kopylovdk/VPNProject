from datetime import datetime, timedelta
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
    is_admin = models.BooleanField(verbose_name='Администратор', default=False)

    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)

    def __str__(self):
        return f'{self.telegram_login!r}_{self.telegram_id!r}'

    # TODO: Need test
    def change_is_admin(self) -> None:
        if self.is_admin:
            self.is_admin = False
        else:
            self.is_admin = True
        self.save()


class OutlineVPNKeys(models.Model):
    class Meta:
        db_table = 'OutlineVPNKeys'
        verbose_name = 'Outline VPN Key'
        verbose_name_plural = 'Outline VPN Keys'
        constraints = [
            models.UniqueConstraint(
                fields=['outline_key_id'],
                name='unique_outline_key_id'
            )
        ]

    # class ServerCountries(models.TextChoices):
    #     KZ = 'KZ', 'KZ'

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
    outline_key_traffic_limit = models.BigIntegerField(verbose_name='Лимит трафика', null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    # TODO: Если нужна будет информация о стране, где будет находится VPN сервер
    # outline_vpn_key_server_country = models.CharField(
    #     verbose_name='Страна нахождения VPN Сервера',
    #     max_length=64,
    #     choices=ServerCountries.choices,
    #     null=True,
    #     blank=True,
    # )

    def __str__(self):
        return f'{self.telegram_user_record!r}_{self.outline_key_name!r}'

    def add_tg_user(self, telegram_user: TelegramUsers) -> None:
        """
        Метод добавления TelegramUsers в запись OutlineVPNKeys
        Params:
            telegram_user: TelegramUsers
        Returns: none
        Exceptions: None
        """
        self.telegram_user_record = telegram_user
        self.save()

    def change_active_status(self) -> bool:
        """
        Метод изменения статуса записи OutlineVPNKeys
        Params: None
        Returns: bool
        Exceptions: None
        """
        if self.outline_key_active:
            self.outline_key_active = False
        else:
            self.outline_key_active = True
        self.save()
        return self.outline_key_active

    def change_valid_until(self, days: int) -> datetime or None:
        """
        Метод изменения срока действия записи OutlineVPNKeys
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

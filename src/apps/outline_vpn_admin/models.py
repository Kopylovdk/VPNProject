from datetime import datetime, timedelta
from django.db import models
from django.contrib.postgres.fields import JSONField


class Client(models.Model):
    class Meta:
        db_table = 'Client'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    full_name = models.CharField(verbose_name='ФИО', max_length=254, null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def __str__(self):
        return self.full_name or "Empty"


class Transport(models.Model):
    class Meta:
        db_table = 'Transport'
        verbose_name = 'Transport'
        verbose_name_plural = 'Transports'

    transport_name = models.CharField(verbose_name='Название бота', max_length=254, null=True, blank=True)
    transport_credentials = JSONField(verbose_name='Реквизиты бота')
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def __str__(self):
        return self.transport_name


class Contact(models.Model):
    class Meta:
        db_table = 'Contact'
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Владелец ключа', null=True, blank=True)
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE, verbose_name='Канал связи')
    contact_name = models.CharField(verbose_name='Название контакта', max_length=254, null=True, blank=True)
    contact_credentials = JSONField(verbose_name='Реквизиты пользователя', null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def __str__(self):
        return f'{self.client}_{self.contact_name}_{self.transport}'


class VPNServer(models.Model):
    class Meta:
        db_table = 'VPNServer'
        verbose_name = 'VPNServer'
        verbose_name_plural = 'VPNServers'

    server_name = models.CharField(verbose_name='Название VPN сервера', max_length=254, null=True, blank=True)
    server_credentials = JSONField(verbose_name='Реквизиты впн', null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def __str__(self):
        return self.server_name


class VPNToken(models.Model):
    class Meta:
        db_table = 'VPNToken'
        verbose_name = 'VPNToken'
        verbose_name_plural = 'VPNTokens'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Владелец ключа')
    server = models.ForeignKey(VPNServer, on_delete=models.CASCADE, verbose_name='VPN сервер')
    token_id = models.BigIntegerField(verbose_name='VPN Token ID on VPN Server', null=True, blank=True)
    token_name = models.CharField(verbose_name='Имя VPN ключа', max_length=254, null=True, blank=True)
    token_uri = models.TextField(verbose_name='VPN ключ', null=True, blank=True)
    token_valid_until = models.DateField(verbose_name='Дата окончания подписки', null=True, blank=True)
    token_is_active = models.BooleanField(verbose_name='Активность VPN ключа', default=False)
    token_traffic_limit = models.BigIntegerField(verbose_name='Лимит трафика', null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def change_active_status(self) -> bool:
        """
        Метод изменения статуса записи VPNToken
        Params: None
        Returns: bool
        Exceptions: None
        """
        if self.token_is_active:
            self.token_is_active = False
        else:
            self.token_is_active = True
        self.save()
        return self.token_is_active

    def change_valid_until(self, days: int = 0) -> datetime or None:
        """
        Метод изменения срока действия записи VPNToken. По умолчанию удаляет значение
        Params:
             days: int
        Returns:
            datetime.datetime
        Exceptions: None
        """
        if days:
            self.token_valid_until = self.token_valid_until + timedelta(days=days)
        else:
            self.token_valid_until = None
        self.save()
        return self.token_valid_until

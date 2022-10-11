from django.db import models


class Client(models.Model):
    class Meta:
        db_table = 'Client'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    full_name = models.CharField(verbose_name='ФИО', max_length=254, null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def __repr__(self):
        return f"<{self.__class__.__name__!r} id={self.id!r} name={self.full_name!r}>"


class Transport(models.Model):
    class Meta:
        db_table = 'Transport'
        verbose_name = 'Transport'
        verbose_name_plural = 'Transports'

    name = models.CharField(verbose_name='Название бота', max_length=254, null=True, blank=True)
    credentials = models.JSONField(verbose_name='Реквизиты бота')
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def __repr__(self):
        return f"<{self.__class__.__name__!r} id={self.id!r} name={self.name!r}>"


class Contact(models.Model):
    class Meta:
        db_table = 'Contact'
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Владелец ключа')
    transport = models.ForeignKey(Transport, on_delete=models.RESTRICT, verbose_name='Канал связи')
    name = models.CharField(verbose_name='Название контакта', max_length=254, null=True, blank=True)
    credentials = models.JSONField(verbose_name='Реквизиты пользователя', null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def __repr__(self):
        return f"<{self.__class__.__name__!r} id={self.id!r} name={self.name!r}>"


class VPNServer(models.Model):
    class Meta:
        db_table = 'VPNServer'
        verbose_name = 'VPNServer'
        verbose_name_plural = 'VPNServers'

    name = models.CharField(verbose_name='Название VPN сервера', max_length=254, null=True, blank=True)
    uri = models.CharField(verbose_name='URI для создания ключей OutLine', max_length=254, null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def __repr__(self):
        return f"<{self.__class__.__name__!r} id={self.id!r} name={self.name!r}>"


class VPNToken(models.Model):
    class Meta:
        db_table = 'VPNToken'
        verbose_name = 'VPNToken'
        verbose_name_plural = 'VPNTokens'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Владелец ключа')
    server = models.ForeignKey(VPNServer, on_delete=models.RESTRICT, verbose_name='VPN сервер')
    outline_id = models.BigIntegerField(verbose_name='VPN Token ID on VPN Server', null=True, blank=True)
    name = models.CharField(verbose_name='Имя VPN ключа', max_length=254, null=True, blank=True)
    vpn_key = models.TextField(verbose_name='VPN ключ', null=True, blank=True)
    valid_until = models.DateField(verbose_name='Дата окончания подписки', null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Активность VPN ключа', default=True)
    traffic_limit = models.BigIntegerField(verbose_name='Лимит трафика', null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def __repr__(self):
        return f"<{self.__class__.__name__!r} id={self.id!r} outline_id={self.outline_id!r}>"


class Tariffication(models.Model):
    class Meta:
        db_table = 'Tariffication'
        verbose_name = 'Tariffication'
        verbose_name_plural = 'Tariffications'

    name = models.CharField(verbose_name='Имя тарифа', max_length=254)
    prolong_days = models.IntegerField(verbose_name='Срок продления в днях')
    price = models.DecimalField(verbose_name='Стоимость', max_digits=10, decimal_places=2)
    valid_until = models.DateField(verbose_name='Срок активности тарифа')
    is_active = models.BooleanField(verbose_name='Активность тарифа', default=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def __repr__(self):
        return f"<{self.__class__.__name__!r} id={self.id!r} name={self.name!r}>"

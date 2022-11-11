from django.core.validators import MaxValueValidator
from django.db import models
from django.forms import model_to_dict
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
from django.conf import settings


class DictRepresentationMixin:
    def as_dict(self, exclude: list = None) -> dict:
        """Метод для конвертации Объекта модели в словарь"""
        return model_to_dict(self, exclude=exclude)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Client(models.Model, DictRepresentationMixin):
    class Meta:
        db_table = 'Client'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    full_name = models.CharField(verbose_name='ФИО', max_length=254, null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def is_has_demo(self):
        return self.vpntoken_set.filter(is_demo=True).exists()

    def is_token_owner(self, token_id: int):
        return self.vpntoken_set.filter(id=token_id).exists()

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id!r} name={self.full_name!r}>"

    def __str__(self):
        return f'{self.id}_{self.full_name if self.full_name else ""}'


class Transport(models.Model, DictRepresentationMixin):
    class Meta:
        db_table = 'Transport'
        verbose_name = 'Transport'
        verbose_name_plural = 'Transports'

    name = models.CharField(verbose_name='Название бота', max_length=254)

    uid_format = models.CharField(
        verbose_name='Формат уникального идентификатора бота',
        max_length=254,
        blank=False,
        help_text='Наименование уникального идентификатора в credentials. {поле_уникального_идентификатора}',
    )
    full_name_format = models.CharField(
        verbose_name='Формат имени клиента',
        max_length=254,
        default='',
        help_text='Наименование полей в credentials для формирования имени клиента. {Поле_1} {Поле_2} и т.д.',
    )
    credentials = models.JSONField(verbose_name='Реквизиты бота')
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id!r} name={self.name!r}>"

    def make_contact_credentials_uid(self, contact_credentials: dict):
        return f'{self.name}@{self.uid_format}'.format(**contact_credentials)

    def make_contact_messenger_id_uid(self, messenger_id: int):
        return f'{self.name}@{messenger_id}'

    def fill_client_details(self, client: Client, contact_credentials: dict):
        client.full_name = f'{self.full_name_format}'.format(**contact_credentials)
        client.save()
        return client

    def __str__(self):
        return self.name


class Contact(models.Model, DictRepresentationMixin):
    class Meta:
        db_table = 'Contact'
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Владелец ключа')
    transport = models.ForeignKey(Transport, on_delete=models.RESTRICT, verbose_name='Канал связи')
    uid = models.CharField(
        verbose_name='Идентификатор контакта',
        max_length=254,
        help_text='<Transport.name>@<Transport.uid_format>'
    )
    name = models.CharField(verbose_name='Название контакта', max_length=254, null=True, blank=True)
    phone_number = models.CharField(verbose_name='Номер телефона', max_length=20, null=True, blank=True)
    credentials = models.JSONField(verbose_name='Реквизиты пользователя', null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id!r} name={self.name!r}>"

    def save(self, **kwargs):
        if not self.uid:
            self.uid = self.transport.make_contact_credentials_uid(self.credentials)
        super().save(**kwargs)


class VPNServer(models.Model, DictRepresentationMixin):
    class Meta:
        db_table = 'VPNServer'
        verbose_name = 'VPNServer'
        verbose_name_plural = 'VPNServers'

    name = models.CharField(verbose_name='Внутреннее имя VPN сервера', max_length=254)
    external_name = models.CharField(verbose_name='Внешнее имя VPN сервера', max_length=254)
    uri = models.CharField(verbose_name='URI для создания ключей OutLine', max_length=254)
    is_default = models.BooleanField(verbose_name='Сервер по умолчанию', default=False)
    is_active = models.BooleanField(verbose_name='Активность', default=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id!r} name={self.name!r}>"

    def __str__(self):
        return self.name


class Currency(models.Model, DictRepresentationMixin):
    class Meta:
        db_table = 'Currency'
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'

    name = models.CharField(verbose_name='Буквенный код валюты по ISO 4217', max_length=3)
    name_iso = models.IntegerField(verbose_name='Цифровой код валюты по ISO 4217', validators=[MaxValueValidator(999)])
    is_main = models.BooleanField(verbose_name='Основная валюта', default=False)
    exchange_rate = models.DecimalField(verbose_name='Курс к основной валюте', max_digits=5, decimal_places=2)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)
    is_active = models.BooleanField(verbose_name='Активность валюты', default=True)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id!r} name={self.name!r}>"

    def __str__(self):
        return self.name


class Tariff(models.Model, DictRepresentationMixin):
    class Meta:
        db_table = 'Tariff'
        verbose_name = 'Tariff'
        verbose_name_plural = 'Tariffs'

    name = models.CharField(verbose_name='Имя тарифа', max_length=254)
    prolong_period = models.IntegerField(verbose_name='Срок продления в днях')
    price = models.DecimalField(verbose_name='Стоимость', max_digits=10, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT, verbose_name='Валюта')
    traffic_limit = models.IntegerField(verbose_name='Ограничение трафика в байтах')
    valid_until = models.DateField(verbose_name='Срок активности тарифа', null=True, blank=True)
    is_demo = models.BooleanField(verbose_name='Демо тариф', default=False)
    is_tech = models.BooleanField(verbose_name='Технический тариф', default=False)
    is_active = models.BooleanField(verbose_name='Активность тарифа', default=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id!r} name={self.name!r}>"


class VPNToken(models.Model, DictRepresentationMixin):
    class Meta:
        db_table = 'VPNToken'
        verbose_name = 'VPNToken'
        verbose_name_plural = 'VPNTokens'

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Владелец ключа')
    server = models.ForeignKey(VPNServer, on_delete=models.RESTRICT, verbose_name='VPN сервер')
    tariff = models.ForeignKey(Tariff, on_delete=models.RESTRICT, verbose_name='Тариф')
    outline_id = models.BigIntegerField(verbose_name='VPN Token ID on VPN Server', null=True, blank=True)
    previous_vpn_token_id = models.BigIntegerField(verbose_name='ID предыдущего VPN ключа', null=True, blank=True)
    name = models.CharField(verbose_name='Имя VPN ключа', max_length=254, null=True, blank=True)
    vpn_key = models.TextField(verbose_name='VPN ключ', null=True, blank=True)
    valid_until = models.DateField(verbose_name='Дата окончания подписки', null=True, blank=True)
    is_active = models.BooleanField(verbose_name='Активность VPN ключа', default=True)
    is_demo = models.BooleanField(verbose_name='Демо', default=False)
    traffic_limit = models.BigIntegerField(verbose_name='Лимит трафика', null=True, blank=True)
    created_at = models.DateField(verbose_name='Дата создания записи', auto_now_add=True)
    updated_at = models.DateField(verbose_name='Дата обновления записи', auto_now=True)

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id!r} outline_id={self.outline_id!r}>"


# TODO: Сделать миграции, тесты и дополнить модель полями при подключении оплат
# class Payment(models.Model):
#     class Meta:
#         db_table = 'Payment'
#         verbose_name = 'Payment'
#         verbose_name_plural = 'Payments'
#
#     client = models.ForeignKey(Client, on_delete=models.RESTRICT, verbose_name='Плательщик')
#     vpn_token = models.ForeignKey(VPNToken, on_delete=models.RESTRICT, verbose_name='VPN Ключ')
#     value = models.CharField(verbose_name='Значение', max_length=254)
#     bill = models.CharField(verbose_name='Счет', max_length=254)
#     is_payed = models.BooleanField(verbose_name='Оплачен', default=False)

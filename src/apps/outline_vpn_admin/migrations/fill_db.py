from django.db import migrations
from django.contrib.auth.models import User

from apps.outline_vpn_admin.models import Transport, VPNServer, Tariff, Currency


class Migration(migrations.Migration):
    dependencies = [
        ('outline_vpn_admin', 'create_superuser'),
    ]

    def fill_default_db_data(*args, **kwargs):
        test_client_bot_name = 'test_client_telegram_bot'
        User.objects.create_user(
            username=test_client_bot_name,
            password=test_client_bot_name,
            email=f"{test_client_bot_name}_email@test.ru"
        ).save()

        Transport.objects.create(
            name=test_client_bot_name,
            uid_format='{id}',
            full_name_format='{first_name} {last_name}',
            credentials={"token": "1722461468:AAHi-8QjcE3nvKGrUVkFIFQzdSj1bfN_2Zc"}
        ).save()

        test_admin_bot_name = 'test_admin_telegram_bot'
        User.objects.create_user(
            username=test_admin_bot_name,
            password=test_admin_bot_name,
            email=f"{test_admin_bot_name}_email@test.ru"
        ).save()

        Transport.objects.create(
            name=test_admin_bot_name,
            uid_format='{id}',
            full_name_format='{first_name} {last_name}',
            credentials={"token": "5701018902:AAEFtIgQZSyAde7FOXGtcq_VOq5df-ckxNs"}
        ).save()

        VPNServer.objects.create(
            name='test_vpn_server_in_russia',
            external_name='В России',
            uri='https://62.113.111.75:20125/et_PPlt-7Kz-O0FxVnT4gQ',
        ).save()

        cur_names = ['RUB', 'USD', 'EUR']
        names_iso = [643, 840, 978]
        exchange_rate = [1, 65, 65]
        for i in range(len(cur_names)):
            Currency.objects.create(
                name=cur_names[i],
                name_iso=names_iso[i],
                exchange_rate=exchange_rate[i],
                is_main=True if cur_names[i] in 'RUB' else False,
            ).save()

        prolong_periods = [7, 92, 183, 0]
        traffic_limits = [1073741824, 0, 0, 0]
        prices = [0, 1350, 1500, 0]
        months = [0, 3, 6, 0]
        months_names = ['Demo', 'месяца', 'месяцев', 'Tech']

        currency = Currency.objects.get(name='RUB')
        for i in range(len(months_names)):
            if months[i] == 0:
                name = f'{months_names[i]}'
            else:
                name = f'{months[i]} {months_names[i]}'
            Tariff.objects.create(
                name=name,
                prolong_period=prolong_periods[i],
                price=prices[i],
                traffic_limit=traffic_limits[i],
                currency=currency,
                is_demo=True if name in "Demo" else False,
                is_tech=True if name in "Tech" else False,
            ).save()

    operations = [
        migrations.RunPython(fill_default_db_data),
    ]

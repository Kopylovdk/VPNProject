from django.db import migrations
from django.contrib.auth.models import User

from apps.outline_vpn_admin.models import Transport, VPNServer, Tariff, Currency


class Migration(migrations.Migration):
    dependencies = [
        ('outline_vpn_admin', 'create_superuser'),
        ('outline_vpn_admin', '0004_alter_transport_is_admin_transport'),
    ]

    def fill_test_db_data(*args, **kwargs):
        test_bots_name = [
            'test_client_telegram_bot',
            'test_admin_telegram_bot',
        ]
        test_bots_api = [
            {"token": "1722461468:AAHi-8QjcE3nvKGrUVkFIFQzdSj1bfN_2Zc"},
            {"token": "5768409931:AAFVnYUYpTAkAcwkqchjNB-r2f5oy-t3BL8"},
        ]

        for test_bot_cnt in range(len(test_bots_name)):
            User.objects.create_user(
                username=test_bots_name[test_bot_cnt],
                password=test_bots_name[test_bot_cnt],
                email=f"{test_bots_name[test_bot_cnt]}_email@test.ru"
            ).save()

            Transport.objects.create(
                name=test_bots_name[test_bot_cnt],
                uid_format='{id}',
                full_name_format='{first_name} {last_name}',
                credentials=test_bots_api[test_bot_cnt],
                is_admin_transport=True if "admin" in test_bots_name[test_bot_cnt] else False,
            ).save()

        VPNServer.objects.create(
            name='test_vpn_server_in_russia',
            external_name='В России',
            uri='вставить url для тестового сервера',
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
                prolong_period=prolong_periods[i] if prolong_periods[i] else None,
                price=prices[i],
                traffic_limit=traffic_limits[i] if traffic_limits[i] else None,
                currency=currency,
                is_demo=True if name in "Demo" else False,
                is_tech=True if name in "Tech" else False,
            ).save()

    operations = [
        migrations.RunPython(fill_test_db_data),
    ]

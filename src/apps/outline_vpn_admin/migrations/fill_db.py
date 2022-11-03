from django.db import migrations
from django.contrib.auth.models import User

from apps.outline_vpn_admin.models import Transport, VPNServer, Tariff


class Migration(migrations.Migration):
    dependencies = [
        ('outline_vpn_admin', 'create_superuser'),
    ]

    def fill_default_db_data(*args, **kwargs):
        test_bot_name = 'test_telegram_bot'
        User.objects.create_user(
            username=test_bot_name,
            password=test_bot_name,
            email="test_bot_admin_email@test.ru"
        ).save()

        Transport.objects.create(
            name=test_bot_name,
            uid_format='{id}',
            full_name_format='{first_name} {last_name}',
            credentials={"token": "1722461468:AAHi-8QjcE3nvKGrUVkFIFQzdSj1bfN_2Zc"}
        ).save()

        VPNServer.objects.create(
            name='test_vpn_server_name',
            external_name='test_vpn_server_external_name',
            uri='https://62.113.111.75:20125/et_PPlt-7Kz-O0FxVnT4gQ',
        ).save()

        prolong_periods = [7, 90, 180]
        prices = [0, 1350, 1500]
        months = [0, 3, 6]
        months_names = ['demo', 'месяца', 'месяцев']

        for i in range(3):
            if months[i] == 0:
                name = f'{months_names[i]}'
            else:
                name = f'{months[i]} {months_names[i]}'
            Tariff.objects.create(
                name=name,
                prolong_period=prolong_periods[i],
                price=prices[i],
            ).save()

    operations = [
        migrations.RunPython(fill_default_db_data),
    ]

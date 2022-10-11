# Generated by Django 4.1.2 on 2022-10-11 15:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(blank=True, max_length=254, null=True, verbose_name='ФИО')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Дата создания записи')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Дата обновления записи')),
            ],
            options={
                'verbose_name': 'Client',
                'verbose_name_plural': 'Clients',
                'db_table': 'Client',
            },
        ),
        migrations.CreateModel(
            name='Tariffication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254, verbose_name='Имя тарифа')),
                ('prolong_days', models.IntegerField(verbose_name='Срок продления в днях')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='Стоимость')),
                ('valid_until', models.DateField(verbose_name='Срок активности тарифа')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активность тарифа')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Дата создания записи')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Дата обновления записи')),
            ],
            options={
                'verbose_name': 'Tariffication',
                'verbose_name_plural': 'Tariffications',
                'db_table': 'Tariffication',
            },
        ),
        migrations.CreateModel(
            name='Transport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=254, null=True, verbose_name='Название бота')),
                ('credentials', models.JSONField(verbose_name='Реквизиты бота')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Дата создания записи')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Дата обновления записи')),
            ],
            options={
                'verbose_name': 'Transport',
                'verbose_name_plural': 'Transports',
                'db_table': 'Transport',
            },
        ),
        migrations.CreateModel(
            name='VPNServer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=254, null=True, verbose_name='Название VPN сервера')),
                ('uri', models.CharField(blank=True, max_length=254, null=True, verbose_name='URI для создания ключей OutLine')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Дата создания записи')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Дата обновления записи')),
            ],
            options={
                'verbose_name': 'VPNServer',
                'verbose_name_plural': 'VPNServers',
                'db_table': 'VPNServer',
            },
        ),
        migrations.CreateModel(
            name='VPNToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('outline_id', models.BigIntegerField(blank=True, null=True, verbose_name='VPN Token ID on VPN Server')),
                ('name', models.CharField(blank=True, max_length=254, null=True, verbose_name='Имя VPN ключа')),
                ('vpn_key', models.TextField(blank=True, null=True, verbose_name='VPN ключ')),
                ('valid_until', models.DateField(blank=True, null=True, verbose_name='Дата окончания подписки')),
                ('is_active', models.BooleanField(default=True, verbose_name='Активность VPN ключа')),
                ('traffic_limit', models.BigIntegerField(blank=True, null=True, verbose_name='Лимит трафика')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Дата создания записи')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Дата обновления записи')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='outline_vpn_admin.client', verbose_name='Владелец ключа')),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='outline_vpn_admin.vpnserver', verbose_name='VPN сервер')),
            ],
            options={
                'verbose_name': 'VPNToken',
                'verbose_name_plural': 'VPNTokens',
                'db_table': 'VPNToken',
            },
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=254, null=True, verbose_name='Название контакта')),
                ('credentials', models.JSONField(blank=True, null=True, verbose_name='Реквизиты пользователя')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Дата создания записи')),
                ('updated_at', models.DateField(auto_now=True, verbose_name='Дата обновления записи')),
                ('client', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='outline_vpn_admin.client', verbose_name='Владелец ключа')),
                ('transport', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='outline_vpn_admin.transport', verbose_name='Канал связи')),
            ],
            options={
                'verbose_name': 'Contact',
                'verbose_name_plural': 'Contacts',
                'db_table': 'Contact',
            },
        ),
    ]

# Generated by Django 4.1.3 on 2022-11-18 13:10

import apps.outline_vpn_admin.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('outline_vpn_admin', 'create_superuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='TokenProcess',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('script_name', models.CharField(max_length=254, verbose_name='Имя скрипта, добавившего запись')),
                ('text', models.TextField(verbose_name='Текст сообщения')),
                ('is_executed', models.BooleanField(default=False, verbose_name='Выполнено')),
                ('executed_at', models.DateField(blank=True, null=True, verbose_name='Дата создания записи')),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Дата создания записи')),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='outline_vpn_admin.contact', verbose_name='Контакт пользователя')),
                ('transport', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='outline_vpn_admin.transport', verbose_name='Канал связи')),
                ('vpn_server', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='outline_vpn_admin.vpnserver', verbose_name='VPN сервер')),
                ('vpn_token', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='outline_vpn_admin.vpntoken', verbose_name='VPN токен')),
            ],
            options={
                'verbose_name': 'TokenProcess',
                'verbose_name_plural': 'TokenProcesses',
                'db_table': 'TokenProcess',
            },
            bases=(models.Model, apps.outline_vpn_admin.models.DictRepresentationMixin),
        ),
    ]

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramUsers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_id', models.IntegerField(null=True, verbose_name='ID пользователя телеграм')),
                ('telegram_login', models.CharField(blank=True, max_length=254, null=True, verbose_name='Логин телеграм')),
                ('telegram_first_name', models.CharField(blank=True, max_length=254, null=True, verbose_name='Имя телеграм')),
                ('telegram_last_name', models.CharField(blank=True, max_length=254, null=True, verbose_name='Фамилия телеграм')),
                ('is_admin', models.BooleanField(verbose_name='Администратор', default=False)),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Дата создания записи')),
            ],
            options={
                'db_table': 'TelegramUsers',
                'verbose_name': 'Telegram User',
                'verbose_name_plural': 'Telegram Users',
            },
        ),
        migrations.CreateModel(
            name='OutlineVPNKeys',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_user_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='service.TelegramUsers', verbose_name='Владелец ключа', null=True, blank=True)),
                ('outline_key_id', models.IntegerField(blank=True, null=True, verbose_name='ID OutLine VPN Key')),
                ('outline_key_value', models.CharField(verbose_name='VPN ключ', max_length=254, null=True, blank=True)),
                ('outline_key_name', models.CharField(blank=True, max_length=254, null=True, verbose_name='Имя VPN ключа', default='Отсутствует')),
                ('outline_key_valid_until', models.DateField(blank=True, null=True, verbose_name='Дата окончания подписки')),
                ('outline_key_active', models.BooleanField(default=False, verbose_name='Активность VPN ключа')),
                ('outline_key_traffic_limit', models.IntegerField(verbose_name='Лимит трафика', null=True, blank=True)),
                ('created_at', models.DateField(auto_now_add=True, verbose_name='Дата создания записи')),
            ],
            options={
                'db_table': 'OutlineVPNKeys',
                'verbose_name': 'Outline VPN Key',
                'verbose_name_plural': 'Outline VPN Keys',
            },
        ),
        migrations.AddConstraint(
            model_name='TelegramUsers',
            constraint=models.UniqueConstraint(fields=('telegram_id',), name='unique_telegram_id'),
        ),
        migrations.AddConstraint(
            model_name='OutlineVPNKeys',
            constraint=models.UniqueConstraint(fields=('outline_key_id',), name='unique_outline_key_id'),
        ),
    ]

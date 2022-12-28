from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outline_vpn_admin', '0006_alter_tariff_traffic_limit'),
    ]

    operations = [
        migrations.AddField(
            model_name='vpntoken',
            name='traffic_used',
            field=models.BigIntegerField(null=True, blank=True, verbose_name='Использовано трафика, байт'),
        ),
        migrations.AddField(
            model_name='vpntoken',
            name='traffic_last_update',
            field=models.DateTimeField(null=True, blank=True, verbose_name='Последнее обновление использованного трафика'),
        ),
    ]

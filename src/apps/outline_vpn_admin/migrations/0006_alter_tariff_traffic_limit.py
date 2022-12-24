from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outline_vpn_admin', '0005_alter_tokenprocess_executed_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tariff',
            name='traffic_limit',
            field=models.BigIntegerField(null=True, blank=True, verbose_name='Ограничение трафика в байтах'),
        ),
    ]

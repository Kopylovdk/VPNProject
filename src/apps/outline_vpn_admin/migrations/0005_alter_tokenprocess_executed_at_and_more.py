from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('outline_vpn_admin', 'fill_db'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokenprocess',
            name='executed_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата выполнения'),
        ),
        migrations.AlterField(
            model_name='vpntoken',
            name='valid_until',
            field=models.DateField(blank=True, null=True, verbose_name='Дата окончания подписки'),
        ),
    ]

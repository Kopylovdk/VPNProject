# Generated by Django 4.1.4 on 2022-12-12 09:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('outline_vpn_admin', '0002_alter_contact_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='transport',
            name='is_active',
            field=models.BooleanField(verbose_name='Активность', default=True)
        ),
    ]

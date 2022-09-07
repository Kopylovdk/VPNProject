from django.db import migrations
from django.contrib.auth.models import User


class Migration(migrations.Migration):
    dependencies = [
        ('outline_vpn_admin', '0001_initial'),
    ]

    def generate_superuser(*args, **kwargs):
        User.objects.create_superuser(
            username='admin',
            email='admin@admin.ru',
            password='admin').save()

    operations = [
        migrations.RunPython(generate_superuser),
    ]

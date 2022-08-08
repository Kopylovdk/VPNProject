import datetime

from apps.service.models import VPNServiceRecord


def create_services(cnt: int = 1):
    services = []
    for service_cnt in range(cnt):
        to_create = VPNServiceRecord(
            telegram_id=service_cnt,
            telegram_login=f'tg login test_{service_cnt}',
            telegram_first_name=f'tg first_name test_{service_cnt}',
            telegram_last_name=f'tg last_name test_{service_cnt}',
            outline_key_id=service_cnt,
            outline_key_created_at=datetime.datetime.now(),
            outline_key_valid_until=datetime.datetime.now() + datetime.timedelta(days=60),
        )
        to_create.save()
        services.append(to_create)
    return services

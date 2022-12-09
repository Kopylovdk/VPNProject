import datetime

_cache_update_date = None


def get_actual_cache_date() -> datetime.datetime:
    """Корректно только для случая, когда админка запущена в единичном экземпляре"""
    global _cache_update_date
    if _cache_update_date is not None:
        return _cache_update_date
    from apps.outline_vpn_admin.models import Tariff, Transport, VPNServer
    update_cache_date(Tariff.objects.order_by('-updated_at').only('updated_at').first().updated_at)
    update_cache_date(Transport.objects.order_by('-updated_at').only('updated_at').first().updated_at)
    update_cache_date(VPNServer.objects.order_by('-updated_at').only('updated_at').first().updated_at)


def update_cache_date(new_date: datetime.datetime):
    global _cache_update_date
    _cache_update_date = _cache_update_date and max(_cache_update_date, new_date) or new_date

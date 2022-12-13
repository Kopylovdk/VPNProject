import datetime
from apps.outline_vpn_admin.models import Tariff, Transport, VPNServer
from django.db.models import Max
import logging

log = logging.getLogger(__name__)


def get_actual_cache_date() -> datetime:
    cache_update_date_tariff = Tariff.objects.aggregate(Max('updated_at'))
    cache_update_date_transport = Transport.objects.aggregate(Max('updated_at'))
    cache_update_date_vpnserver = VPNServer.objects.aggregate(Max('updated_at'))
    cache_update_date_max = max(
        cache_update_date_tariff["updated_at__max"],
        cache_update_date_transport["updated_at__max"],
        cache_update_date_vpnserver["updated_at__max"]
    )
    return cache_update_date_max

from django.contrib import admin

from apps.service.models import TelegramUsers, OutlineVPNKeys


@admin.register(TelegramUsers)
class VPNServiceRecordAdmin(admin.ModelAdmin):
    pass


@admin.register(OutlineVPNKeys)
class VPNServiceRecordAdmin(admin.ModelAdmin):
    pass
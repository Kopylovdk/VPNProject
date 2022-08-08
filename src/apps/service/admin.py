from django.contrib import admin

from apps.service.models import VPNServiceRecord

@admin.register(VPNServiceRecord)
class VPNServiceRecordAdmin(admin.ModelAdmin):
    pass

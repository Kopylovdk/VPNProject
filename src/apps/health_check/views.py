from django.http import HttpResponse
from django.views.generic import View
import logging


log = logging.getLogger(__name__)


class HealthCheckView(View):
    http_method_names = ['get']

    def get(self, *args, **kwargs):
        log.info('test page request')
        return HttpResponse(status=200)

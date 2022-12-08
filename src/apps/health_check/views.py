import logging
from rest_framework import views
from rest_framework import status
from rest_framework.response import Response

log = logging.getLogger(__name__)


class HealthCheckView(views.APIView):
    def get(self, *args, **kwargs):
        log.info('test page request')
        return Response({"details": "Health check"}, status=status.HTTP_200_OK)

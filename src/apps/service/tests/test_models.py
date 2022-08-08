from django.test import TestCase
from apps.service.tests import helpers
from apps.service.models import VPNServiceRecord


class ServiceTestCase(TestCase):
    def test_create_service_ok(self):
        services_to_create = 100
        self.assertEqual(services_to_create, len(helpers.create_services(services_to_create)))
        services_from_db = VPNServiceRecord.objects.all()
        self.assertEqual(services_to_create, len(services_from_db))

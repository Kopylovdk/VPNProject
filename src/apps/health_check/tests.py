from django.urls import reverse
from rest_framework.test import APITestCase


class HealthCheckTestCase(APITestCase):
    def test_health_check(self):
        url = reverse('health_check:check')
        response = self.client.get(url, format='json')
        self.assertEqual(200, response.status_code)

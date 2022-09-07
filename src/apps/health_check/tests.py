from django.test import TestCase


class HealthCheckTestCase(TestCase):

    def test_health_check(self):
        response = self.client.get('/health/check', follow=True)
        self.assertEqual(response.status_code, 200)

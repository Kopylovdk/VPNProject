# from rest_framework.test import APIClient
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APITestCase
# import apps.outline_vpn_admin.tests.helpers as helpers
#
# client = APIClient()
# client.force_authenticate(user=None, token=None)
#
#
# class AccountTests(APITestCase):
#     def test_get_tg_user_error(self):
#         tg_id = helpers.create_telegram_users()[0].telegram_id
#         url = reverse('api:get_user', kwargs={'tg_id': tg_id})
#         response = client.get(url, format='json')
#         print(response.status_code)
#         print(response)
#         # self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         # self.assertEqual(Account.objects.count(), 1)
#         # self.assertEqual(Account.objects.get().name, 'DabApps')
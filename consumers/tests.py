from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

class ConsumerAPITestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_get_consumers(self):
        url = reverse('consumer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_pagination(self):
        url = reverse('consumer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if 'next' key is present in the response
        self.assertIn('next', response.data)
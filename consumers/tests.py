from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from consumers.models import Consumer
from consumers.views import ConsumerListView

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

    def test_rate_limit(self):
        # Make 60 requests within 60 seconds, which should be allowed
        for _ in range(60):
            url = reverse('consumer-list')
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Make an additional request, which should be rate-limited
        url = reverse('consumer-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_import_data_from_csv(self):
        # Run the import_data_from_csv method
        ConsumerListView().import_data_from_csv()

        # Check if the data from the CSV file has been imported correctly
        consumers_count = Consumer.objects.count()
        self.assertEqual(consumers_count, 2)  # Assuming 2 rows in the CSV file

        # Check if the attributes of the first Consumer object match the data in the CSV file
        first_consumer = Consumer.objects.first()
        self.assertEqual(first_consumer.street, "579 Mission Trl")
        self.assertEqual(first_consumer.status, "collected")
        self.assertEqual(first_consumer.previous_jobs_count, 1)
        self.assertEqual(first_consumer.amount_due, 1000)
        self.assertAlmostEqual(first_consumer.lat, 33.38935574)
        self.assertAlmostEqual(first_consumer.lng, -112.0882128)

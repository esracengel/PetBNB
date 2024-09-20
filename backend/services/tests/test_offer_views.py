from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from services.models import ServiceRequest, ServiceOffer
from datetime import date
User = get_user_model()

class ServiceOfferViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create a regular user (service requester)
        self.user = User.objects.create_user(email='requester@testusers.com', username = 'requester', password='testpass123', user_type = "petowner")
        # Create a caregiver user
        self.caregiver = User.objects.create_user(email='caregiver@testusers.com', username = 'caregiver', password='testpass123', user_type = 'caregiver')
        # Create an admin user
        self.admin = User.objects.create_superuser(email='admin@testusers.com', username = 'admin', password='adminpass123', user_type = "staff")
        # Create a service request
        self.service_request = ServiceRequest.objects.create(
            owner=self.user,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 5),
            pet_type='Dog',
            pet_breed='Labrador',
            location='New York',
            description='Need dog sitting',
            is_active=True
        )
        self.offer_data = {
            'service_request': self.service_request.id,
            'price': '50.00',
            'message': 'I can take care of your dog'
        }
        self.url = reverse('serviceoffer-list')

    def test_create_offer_as_caregiver(self):
        # Test that a caregiver can create an offer
        self.client.force_authenticate(user=self.caregiver)
        response = self.client.post(self.url, self.offer_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ServiceOffer.objects.count(), 1)

    def test_create_offer_as_non_caregiver(self):
        # Test that a non-caregiver user cannot create an offer
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.offer_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_offers_as_requester(self):
        # Test that a service requester can list offers for their request
        ServiceOffer.objects.create(service_request=self.service_request, caregiver=self.caregiver, price=50.00, message='Offer 1')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_offers_as_caregiver(self):
        # Test that a caregiver can list their own offers
        offer = ServiceOffer.objects.create(service_request=self.service_request, caregiver=self.caregiver, price=50.00, message='Offer 1')
        self.client.force_authenticate(user=self.caregiver)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], offer.id)

    def test_update_own_offer_as_caregiver(self):
        # Test that a caregiver can update their own offer
        offer = ServiceOffer.objects.create(service_request=self.service_request, caregiver=self.caregiver, price=50.00, message='Offer 1')
        self.client.force_authenticate(user=self.caregiver)
        url = reverse('serviceoffer-detail', kwargs={'pk': offer.id})
        response = self.client.patch(url, {'price': '60.00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ServiceOffer.objects.get(id=offer.id).price, 60.00)

    def test_update_other_offer_as_caregiver(self):
        # Test that a caregiver cannot update another caregiver's offer
        other_caregiver = User.objects.create_user(username='other_caregiver', password='testpass123', user_type = "caregiver")
        offer = ServiceOffer.objects.create(service_request=self.service_request, caregiver=other_caregiver, price=50.00, message='Offer 1')
        self.client.force_authenticate(user=self.caregiver)
        url = reverse('serviceoffer-detail', kwargs={'pk': offer.id})
        response = self.client.patch(url, {'price': '60.00'})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_offer_as_caregiver(self):
        # Test that a caregiver can delete their own offer
        offer = ServiceOffer.objects.create(service_request=self.service_request, caregiver=self.caregiver, price=50.00, message='Offer 1')
        self.client.force_authenticate(user=self.caregiver)
        url = reverse('serviceoffer-detail', kwargs={'pk': offer.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ServiceOffer.objects.count(), 0)

    def test_admin_full_access(self):
        # Test that an admin has full access to all offers
        offer = ServiceOffer.objects.create(service_request=self.service_request, caregiver=self.caregiver, price=50.00, message='Offer 1')
        self.client.force_authenticate(user=self.admin)
        # List all offers
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        # Update any offer
        url = reverse('serviceoffer-detail', kwargs={'pk': offer.id})
        response = self.client.patch(url, {'price': '70.00'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Delete any offer
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_create_offer_for_inactive_request(self):
        # Test that an offer cannot be created for an inactive service request
        self.service_request.is_active = False
        self.service_request.save()
        self.client.force_authenticate(user=self.caregiver)
        response = self.client.post(self.url, self.offer_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
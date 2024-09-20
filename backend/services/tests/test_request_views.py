from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from services.models import ServiceRequest
from datetime import date

User = get_user_model()

class ServiceRequestViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', email = "testuser@test.com", password='testpass123', user_type = "petowner")
        self.admin_user = User.objects.create_superuser(username='admin',email = "admin@test.com", password='adminpass123', user_type = "petowner")
        self.other_user = User.objects.create_user(username='otheruser', email = "otheruser@test.com",password='otherpass123', user_type = "petowner")
        self.client.force_authenticate(user=self.user)
        self.service_request_data = {
            'start_date': '2024-08-01',
            'end_date': '2024-08-05',
            'pet_type': 'Dog',
            'pet_breed': 'Labrador',
            'location': 'New York',
            'description': 'Need someone to take care of my dog for 5 days.',
            'is_active': True
        }
        self.url = reverse('servicerequest-list')
        
        self.caregiver_user = User.objects.create_user(username='caregiver',email = "caregiver@test.com", password='caregiverpass123', user_type = "caregiver")
        

    def test_create_service_request(self):
        # Test creating a new service request
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url, self.service_request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ServiceRequest.objects.count(), 1)
        self.assertEqual(ServiceRequest.objects.get().owner, self.user)

    def test_list_service_requests(self):
        # Test listing service requests (should only see own requests)
        ServiceRequest.objects.create(owner=self.user, **self.service_request_data)
        ServiceRequest.objects.create(owner=self.other_user, **self.service_request_data)
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Changed to 1 as user should only see their own requests

    def test_retrieve_service_request(self):
        # Test retrieving a specific service request
        service_request = ServiceRequest.objects.create(owner=self.user, **self.service_request_data)
        url = reverse('servicerequest-detail', kwargs={'pk': service_request.pk})
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['pet_type'], 'Dog')

    def test_update_service_request(self):
        # Test updating a service request
        service_request = ServiceRequest.objects.create(owner=self.user, **self.service_request_data)
        url = reverse('servicerequest-detail', kwargs={'pk': service_request.pk})
        updated_data = self.service_request_data.copy()
        updated_data['pet_type'] = 'Cat'
        self.client.force_authenticate(user=self.user)
        response = self.client.put(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ServiceRequest.objects.get(pk=service_request.pk).pet_type, 'Cat')

    def test_partial_update_service_request(self):
        # Test partially updating a service request
        service_request = ServiceRequest.objects.create(owner=self.user, **self.service_request_data)
        self.client.force_authenticate(user=self.user)
        url = reverse('servicerequest-detail', kwargs={'pk': service_request.pk})
        response = self.client.patch(url, {'pet_breed': 'Golden Retriever'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ServiceRequest.objects.get(pk=service_request.pk).pet_breed, 'Golden Retriever')

    def test_delete_service_request(self):
        # Test deleting a service request
        service_request = ServiceRequest.objects.create(owner=self.user, **self.service_request_data)
        url = reverse('servicerequest-detail', kwargs={'pk': service_request.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ServiceRequest.objects.count(), 0)

    def test_filter_service_requests(self):
        # Test filtering service requests
        ServiceRequest.objects.create(owner=self.user, **self.service_request_data)
        ServiceRequest.objects.create(
            owner=self.user,
            start_date='2024-09-01',
            end_date='2024-09-05',
            pet_type='Cat',
            pet_breed='Siamese',
            location='Los Angeles',
            description='Cat sitting needed',
            is_active=True
        )
        
        # Test filtering by pet_type
        response = self.client.get(f"{self.url}?pet_type=Dog")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['pet_type'], 'Dog')
        
        # Test filtering by location
        response = self.client.get(f"{self.url}?location=Los%20Angeles")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['location'], 'Los Angeles')
        
        # Test filtering by date range
        response = self.client.get(f"{self.url}?start_date=2024-08-15&end_date=2024-09-30")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['start_date'], '2024-09-01')

    def test_admin_list_all_service_requests(self):
        # Test admin ability to list all service requests
        ServiceRequest.objects.create(owner=self.user, **self.service_request_data)
        ServiceRequest.objects.create(owner=self.other_user, **self.service_request_data)
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_cannot_update_other_user_request(self):
        # Test that a user cannot update another user's service request
        service_request = ServiceRequest.objects.create(owner=self.other_user, **self.service_request_data)
        self.client.force_authenticate(user=self.user)
        updated_data = self.service_request_data.copy()
        updated_data['pet_type'] = 'Cat'
        updated_data['pet_breed'] = 'Siamese'
        self.client.force_authenticate(user=self.user)
        url = reverse('servicerequest-detail', kwargs={'pk': service_request.pk})
        response = self.client.put(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  

    def test_user_cannot_delete_other_user_request(self):
        # Test that a user cannot delete another user's service request
        service_request = ServiceRequest.objects.create(owner=self.other_user, **self.service_request_data)
        self.client.force_authenticate(user=self.user)
        url = reverse('servicerequest-detail', kwargs={'pk': service_request.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)  # Changed to 404 as user can't see other's requests

    def test_admin_can_update_any_request(self):
        # Test that an admin can update any user's service request
        service_request = ServiceRequest.objects.create(owner=self.other_user, **self.service_request_data)
        url = reverse('servicerequest-detail', kwargs={'pk': service_request.pk})
        self.client.force_authenticate(user=self.admin_user)

        updated_data = self.service_request_data.copy()
        updated_data['pet_type'] = 'Cat'
        updated_data['pet_breed'] = 'Siamese'

        response = self.client.put(url, updated_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_service_request = ServiceRequest.objects.get(pk=service_request.pk)
        self.assertEqual(updated_service_request.pet_type, 'Cat')
        self.assertEqual(updated_service_request.pet_breed, 'Siamese')

    def test_admin_can_delete_any_request(self):
        # Test that an admin can delete any user's service request
        service_request = ServiceRequest.objects.create(owner=self.other_user, **self.service_request_data)
        url = reverse('servicerequest-detail', kwargs={'pk': service_request.pk})
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ServiceRequest.objects.count(), 0)
        
    def test_caregiver_access_to_requests(self):
        # Create some service requests
        ServiceRequest.objects.create(owner=self.user, **self.service_request_data)
        ServiceRequest.objects.create(owner=self.other_user, **self.service_request_data)

        # Authenticate as caregiver
        self.client.force_authenticate(user=self.caregiver_user)

        # Test that caregiver can view service requests
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Caregiver should see all requests

        # Test that caregiver cannot create a new service request
        new_request_data = self.service_request_data.copy()
        new_request_data['description'] = 'Caregiver trying to create a request'
        response = self.client.post(self.url, new_request_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify that no new request was created
        self.assertEqual(ServiceRequest.objects.count(), 2)

        # Test that caregiver cannot update an existing service request
        existing_request = ServiceRequest.objects.first()
        update_url = reverse('servicerequest-detail', kwargs={'pk': existing_request.pk})
        update_data = {'description': 'Caregiver trying to update a request'}
        response = self.client.patch(update_url, update_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify that the request was not updated
        existing_request.refresh_from_db()
        self.assertNotEqual(existing_request.description, 'Caregiver trying to update a request')

        # Test that caregiver cannot delete a service request
        delete_url = reverse('servicerequest-detail', kwargs={'pk': existing_request.pk})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Verify that the request was not deleted
        self.assertEqual(ServiceRequest.objects.count(), 2)
        
    def test_search_service_requests(self):
        # Test searching service requests
        
        ServiceRequest.objects.create(
            owner=self.user,
            start_date='2024-08-01',
            end_date='2024-08-05',
            pet_type='Dog',
            pet_breed='Labrador',
            location='New York',
            description='Need dog sitting',
            is_active=True
        )
        ServiceRequest.objects.create(
            owner=self.user,
            start_date='2024-09-01',
            end_date='2024-09-05',
            pet_type='Cat',
            pet_breed='Siamese',
            location='Los Angeles',
            description='Cat sitting needed',
            is_active=True
        )
        response = self.client.get(f"{self.url}?search=dog")
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['pet_type'], 'Dog')

    def test_order_service_requests(self):
        # Test ordering service requests
        
        ServiceRequest.objects.create(
            owner=self.user,
            start_date='2024-08-01',
            end_date='2024-08-05',
            pet_type='Dog',
            pet_breed='Labrador',
            location='New York',
            description='Need dog sitting',
            is_active=True
        )
        ServiceRequest.objects.create(
            owner=self.user,
            start_date='2024-09-01',
            end_date='2024-09-05',
            pet_type='Cat',
            pet_breed='Siamese',
            location='Los Angeles',
            description='Cat sitting needed',
            is_active=True
        )
        response = self.client.get(f"{self.url}?ordering=-start_date")
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['pet_type'], 'Cat')
        self.assertEqual(response.data[1]['pet_type'], 'Dog')
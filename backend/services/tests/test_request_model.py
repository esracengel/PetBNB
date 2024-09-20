from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date
from services.models import ServiceRequest
User = get_user_model()

class ServiceRequestModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        
    def test_service_request_creation(self):
        # Test creation of a ServiceRequest instance with correct attributes
        # Checks: successful creation, string representation, owner, pet details
        service_request = ServiceRequest.objects.create(
            owner=self.user,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 5),
            pet_type='Dog',
            pet_breed='Labrador',
            location='New York',
            description='Need someone to take care of my dog for 5 days.'
        )
        
        self.assertTrue(isinstance(service_request, ServiceRequest))
        self.assertEqual(service_request.__str__(), "Dog care request by testuser")
        self.assertEqual(service_request.owner, self.user)
        self.assertEqual(service_request.pet_type, 'Dog')
        self.assertEqual(service_request.pet_breed, 'Labrador')
        self.assertEqual(service_request.location, 'New York')

    def test_service_request_dates(self):
        # Test that start_date and end_date fields are set correctly
        service_request = ServiceRequest.objects.create(
            owner=self.user,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 5),
            pet_type='Cat',
            pet_breed='Siamese',
            location='Los Angeles',
            description='Cat sitting needed for 5 days.'
        )
        
        self.assertEqual(service_request.start_date, date(2024, 8, 1))
        self.assertEqual(service_request.end_date, date(2024, 8, 5))

    def test_service_request_description(self):
        # Test that the description field can hold a longer text
        long_description = "I need someone to take care of my golden retriever for a week. " \
                           "She's very friendly and needs daily walks. Please make sure to " \
                           "feed her twice a day and give her lots of attention."
        
        service_request = ServiceRequest.objects.create(
            owner=self.user,
            start_date=date(2024, 9, 1),
            end_date=date(2024, 9, 8),
            pet_type='Dog',
            pet_breed='Golden Retriever',
            location='Chicago',
            description=long_description
        )
        
        self.assertEqual(service_request.description, long_description)
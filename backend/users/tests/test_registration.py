from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-list')  # Assuming you're using djoser's default URL name

    def test_user_registration_success(self):
        # Test successful user registration with all required fields
        payload = {
        'email': 'testuser@example.com',
        'username': 'testuser',
        'password': 'testpass123',
        're_password': 'testpass123',  # Add this line
        'user_type': 'petowner',
        'bio': 'Test bio',
        'city': 'Test City',
        'district': 'Test District',
        'birth_date': '1990-01-01',
        'phone_number': '1234567890'
    }
        response = self.client.post(self.register_url, payload)
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='testuser@example.com').exists())
        user = User.objects.get(email='testuser@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.user_type, 'petowner')

    def test_user_registration_missing_required_fields(self):
        # Test registration failure when required fields are missing
        payload = {
            'email': 'testuser@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_invalid_user_type(self):
        # Test registration failure when an invalid user type is provided
        payload = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'user_type': 'invalid_type'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_email(self):
        # Test registration failure when trying to register with an email that's already in use
        User.objects.create_user(email='existing@example.com', username='existing', password='testpass123', user_type='petowner')
        payload = {
            'email': 'existing@example.com',
            'username': 'newuser',
            'password': 'testpass123',
            'user_type': 'petowner'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_weak_password(self):
        # Test registration failure when a weak password is provided
        payload = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': '123',  # Too short/simple
            'user_type': 'petowner'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_invalid_email(self):
        # Test registration failure when an invalid email format is provided
        payload = {
            'email': 'invalidemail',
            'username': 'testuser',
            'password': 'testpass123',
            'user_type': 'petowner'
        }
        response = self.client.post(self.register_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
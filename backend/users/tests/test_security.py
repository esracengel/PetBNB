from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

class UserSecurityTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('user-list')
        self.login_url = reverse('jwt-create')
        self.user_data = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': 'StrongPass123!',
            're_password': 'StrongPass123!',
            'user_type': 'petowner',
        }
        self.user = User.objects.create_user(
            email='existinguser@example.com',
            username='existinguser',
            password='ExistingPass123!',
            user_type='petowner'
        )

    def test_password_hashing(self):
        # Test that passwords are properly hashed
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=self.user_data['email'])
        self.assertNotEqual(user.password, self.user_data['password'])
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))

    def test_password_not_in_response(self):
        # Test that password is not returned in API response
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn('password', response.data)

    def test_login_correct_credentials(self):
        # Test login with correct credentials
        response = self.client.post(self.login_url, {
            'email': 'existinguser@example.com',
            'password': 'ExistingPass123!'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_login_incorrect_credentials(self):
        # Test login with incorrect credentials
        response = self.client.post(self.login_url, {
            'email': 'existinguser@example.com',
            'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_password_complexity(self):
        # Test that weak passwords are rejected
        weak_password_data = self.user_data.copy()
        weak_password_data['password'] = '123'
        weak_password_data['re_password'] = '123'
        response = self.client.post(self.register_url, weak_password_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unique_email(self):
        # Test that duplicate emails are rejected
        duplicate_email_data = self.user_data.copy()
        duplicate_email_data['email'] = 'existinguser@example.com'
        response = self.client.post(self.register_url, duplicate_email_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_auth_required_for_user_detail(self):
        # Test that authentication is required to access user details
        user_detail_url = reverse('user-detail', kwargs={'id': self.user.id})
        response = self.client.get(user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Now try with authentication
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {refresh.access_token}')
        response = self.client.get(user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_cannot_access_other_user_detail(self):
        # Test that a user cannot access another user's details
        other_user = User.objects.create_user(
            email='otheruser@example.com',
            username='otheruser',
            password='OtherPass123!',
            user_type='petowner'
        )
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {refresh.access_token}')
        other_user_detail_url = reverse('user-detail', kwargs={'id': other_user.id})
        response = self.client.get(other_user_detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_password_reset_email_for_non_existent_user(self):
        # Test that password reset doesn't reveal if an email exists
        password_reset_url = reverse('user-reset-password')
        response = self.client.post(password_reset_url, {'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_user_type_validation(self):
        # Test that invalid user types are rejected
        invalid_user_type_data = self.user_data.copy()
        invalid_user_type_data['user_type'] = 'invalid_type'
        response = self.client.post(self.register_url, invalid_user_type_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
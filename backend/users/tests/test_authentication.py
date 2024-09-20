from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class AuthenticationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('jwt-create')
        self.logout_url = reverse('jwt-destroy') 
        self.user_data = {
            'email': 'testuser@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'user_type': 'petowner'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_user_login_success(self):
        """Test successful user login"""
        response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_login_failure(self):
        """Test login failure with incorrect credentials"""
        response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_logout(self):
        """Test user logout (token blacklisting)"""
        # First, login to get the token
        login_response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        # Now, try to blacklist the refresh token
        refresh_token = login_response.data['refresh']
        response = self.client.post(self.logout_url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Try to use the blacklisted token
        refresh_url = reverse('jwt-refresh')
        response = self.client.post(refresh_url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_access_protected_view_with_token(self):
        """Test accessing a protected view with a valid token"""
        
        # First, login to get the token
        login_response = self.client.post(self.login_url, {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)

        # Use the token to access a protected view
        token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {token}')
        protected_url = reverse('user-me')  # Changed from 'user-detail' to 'user-me'
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_protected_view_without_token(self):
        """Test accessing a protected view without a token"""
        
        protected_url = reverse('user-me')  # Changed from 'user-detail' to 'user-me'
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
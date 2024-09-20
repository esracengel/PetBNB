from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'user_type': 'petowner',
            'bio': 'Test bio',
            'city': 'Test City',
            'district': 'Test District',
            'birth_date': '1990-01-01',
            'phone_number': '1234567890'
        }

    def test_create_user(self):
        # Test creating a user with valid data
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.user_type, self.user_data['user_type'])
        self.assertTrue(user.check_password(self.user_data['password']))

    def test_email_is_unique(self):
        # Test that users with duplicate emails cannot be created
        User.objects.create_user(**self.user_data)
        with self.assertRaises(IntegrityError):
            User.objects.create_user(**self.user_data)

    def test_user_type_choices(self):
        # Test that user_type must be one of the predefined choices
        invalid_user = User(email='invalid@example.com', username='invalid', user_type='invalid')
        with self.assertRaises(ValidationError):
            invalid_user.full_clean()

    def test_create_user_without_email(self):
        # Test that creating a user without an email raises an error
        self.user_data.pop('email')
        with self.assertRaises(ValidationError):
            instance = User.objects.create_user(**self.user_data)
            instance.clean()
            instance.save()

    def test_create_superuser(self):
        # Test creating a superuser
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123'
        )
        self.assertTrue(admin_user.is_superuser)
        self.assertTrue(admin_user.is_staff)

    def test_user_str_method(self):
        # Test the string representation of a user
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), self.user_data['email'])

    def test_email_as_username_field(self):
        # Test that email is used as the USERNAME_FIELD
        self.assertEqual(User.USERNAME_FIELD, 'email')

    def test_required_fields(self):
        # Test that username and user_type are in REQUIRED_FIELDS
        self.assertIn('username', User.REQUIRED_FIELDS)
        self.assertIn('user_type', User.REQUIRED_FIELDS)

    def test_optional_fields(self):
        # Test that optional fields can be left blank
        optional_fields = ['bio', 'city', 'district', 'phone_number']
        for field in optional_fields:
            self.user_data[field] = ''

        # Set birth_date to None to test it can be blank
        self.user_data['birth_date'] = None

        user = User.objects.create_user(**self.user_data)
        user.full_clean()  # This should not raise a ValidationError

        # Additional assertions to ensure fields are actually blank or null
        for field in optional_fields:
            self.assertEqual(getattr(user, field), '')
        self.assertIsNone(user.birth_date)
        
    def test_valid_birth_date(self):
        # Test that a valid birth_date is accepted
        user = User.objects.create_user(**self.user_data)
        user.full_clean()
        self.assertEqual(str(user.birth_date), '1990-01-01')
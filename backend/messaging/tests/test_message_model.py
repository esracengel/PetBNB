from django.test import TestCase
from django.contrib.auth import get_user_model
from messaging.models import Message
from django.utils import timezone

User = get_user_model()

class MessageModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='testpass123')

    def test_create_message(self):
        message = Message.objects.create(
            sender=self.user1,
            recipient=self.user2,
            content="Hello, this is a test message."
        )
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.recipient, self.user2)
        self.assertEqual(message.content, "Hello, this is a test message.")
        self.assertFalse(message.is_read)
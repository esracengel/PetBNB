from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from messaging.models import Message

User = get_user_model()

class MessageViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', email='user1@example.com', password='testpass123')
        self.user2 = User.objects.create_user(username='user2', email='user2@example.com', password='testpass123')
        self.client.force_authenticate(user=self.user1)
        self.list_url = reverse('messages-list')

    def test_create_message(self):
        payload = {
            'recipient': self.user2.id,
            'content': 'Test message content'
        }
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)
        message = Message.objects.first()
        self.assertEqual(message.sender, self.user1)
        self.assertEqual(message.recipient, self.user2)
        self.assertEqual(message.content, 'Test message content')

    def test_list_messages(self):
        Message.objects.create(sender=self.user1, recipient=self.user2, content='Message 1')
        Message.objects.create(sender=self.user2, recipient=self.user1, content='Message 2')
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_message(self):
        message = Message.objects.create(sender=self.user1, recipient=self.user2, content='Test message')
        url = reverse('messages-detail', kwargs={'pk': message.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Test message')

    def test_update_message_not_allowed(self):
        message = Message.objects.create(sender=self.user1, recipient=self.user2, content='Original content')
        url = reverse('messages-detail', kwargs={'pk': message.id})
        response = self.client.put(url, {'content': 'Updated content'})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_message_not_allowed(self):
        message = Message.objects.create(sender=self.user1, recipient=self.user2, content='Test message')
        url = reverse('messages-detail', kwargs={'pk': message.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
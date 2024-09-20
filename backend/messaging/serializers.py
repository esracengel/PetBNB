from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')
    recipient_username = serializers.ReadOnlyField(source='recipient.username')

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_username', 'recipient', 'recipient_username', 'content', 'timestamp', 'is_read']
        read_only_fields = ['sender', 'timestamp']
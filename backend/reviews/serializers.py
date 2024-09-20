from rest_framework import serializers
from .models import Review

class ReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.ReadOnlyField(source='reviewer.username')
    reviewee_username = serializers.ReadOnlyField(source='reviewee.username')

    class Meta:
        model = Review
        fields = ['id', 'service', 'reviewer', 'reviewer_username', 'reviewee', 'reviewee_username', 'rating', 'comment', 'created_at']
        read_only_fields = ['reviewer', 'created_at']
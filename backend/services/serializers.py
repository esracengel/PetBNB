from rest_framework import serializers
from .models import ServiceRequest, ServiceOffer
from users.serializers import UserSerializer

class ServiceRequestSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.email', read_only=True)
   
    class Meta:
        model = ServiceRequest
        fields = ['id', 'owner_username', 'start_date', 'end_date', 'pet_type', 'pet_breed', 'location', 'description', 'created_at', 'updated_at', 'is_active']
        read_only_fields = ('owner_username', 'created_at', 'updated_at')
        
class ServiceOfferSerializer(serializers.ModelSerializer):
    caregiver_username = serializers.CharField(source='caregiver.email', read_only=True)

    class Meta:
        model = ServiceOffer
        fields = ['id', 'service_request', 'caregiver_username', 'price', 'message', 'created_at', 'updated_at', 'status']
        read_only_fields = ['caregiver_username', 'created_at', 'updated_at', 'status']

    def create(self, validated_data):
        user = self.context['request'].user
        if user.user_type != "caregiver":
            raise serializers.ValidationError("Only caregivers can make service offers.")
        validated_data['caregiver'] = user
       
        service_request = validated_data['service_request']
        if not service_request.is_active:
            raise serializers.ValidationError("Cannot make an offer for an inactive service request.")
       
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if not instance.service_request.is_active:
            instance.status = 'request_inactive'
        return super().update(instance, validated_data)
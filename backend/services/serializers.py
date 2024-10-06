from rest_framework import serializers
from .models import ServiceRequest, ServiceOffer
from users.serializers import UserSerializer

class ServiceRequestSerializer(serializers.ModelSerializer):
    owner_display_name = serializers.CharField(source='owner.display_name', read_only=True)
    pending_offers_count = serializers.SerializerMethodField()
    total_offers_count = serializers.SerializerMethodField()

    class Meta:
        model = ServiceRequest
        fields = ['id', 'start_date', 'end_date', 'pet_type', 'pet_breed', 'location', 'description', 'is_active', 'owner_display_name', 'owner', 'pending_offers_count', 'created_at', 'updated_at', "total_offers_count"]
        read_only_fields = ['created_at', 'updated_at', 'owner_display_name', 'owner', 'pending_offers_count', "total_offers_count"]

    def get_pending_offers_count(self, obj):
        return ServiceOffer.objects.filter(service_request=obj, status='pending').count()
   
    def get_total_offers_count(self, obj):
        return ServiceOffer.objects.filter(service_request=obj).count()
        
class ServiceOfferSerializer(serializers.ModelSerializer):
    caregiver_username = serializers.CharField(source='caregiver.username', read_only=True)

    class Meta:
        model = ServiceOffer
        fields = ['id', 'service_request', 'caregiver', 'caregiver_username', 'price', 'message', 'created_at', 'updated_at', 'status']
        read_only_fields = ['caregiver_username', 'created_at', 'updated_at', 'status']

    def create(self, validated_data):
        user = self.context['request'].user
        if user.user_type != "caregiver":
            raise serializers.ValidationError("Only caregivers can make service offers.")
        validated_data['caregiver'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if instance.status not in ['pending', 'rejected']:
            raise serializers.ValidationError("Can only update pending or rejected offers.")
        return super().update(instance, validated_data)
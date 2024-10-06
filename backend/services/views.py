from django_filters import rest_framework as filters
from rest_framework import viewsets, permissions, status
from rest_framework import filters as drf_filters
from rest_framework.response import Response
from .models import ServiceRequest, ServiceOffer
from .serializers import ServiceRequestSerializer, ServiceOfferSerializer
from .permissions import IsPetOwnerOrReadOnlyOrAdmin, IsCaregiverOrReadOnlyOrAdmin

class ServiceRequestFilter(filters.FilterSet):
    is_active = filters.BooleanFilter(field_name="is_active")
    location = filters.CharFilter(field_name="location", lookup_expr='icontains')
    pet_breed = filters.CharFilter(field_name="pet_breed", lookup_expr='icontains')
    pet_type = filters.CharFilter(field_name="pet_type", lookup_expr='iexact')
    start_date = filters.DateFilter(field_name="start_date", lookup_expr='gte')
    end_date = filters.DateFilter(field_name="end_date", lookup_expr='lte')
    permission_classes = [permissions.IsAuthenticated, IsPetOwnerOrReadOnlyOrAdmin]

    class Meta:
        model = ServiceRequest
        fields = ['is_active', 'location', 'pet_breed', 'pet_type', 'start_date', 'end_date']

class ServiceRequestViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceRequestSerializer
    permission_classes = [permissions.IsAuthenticated, IsPetOwnerOrReadOnlyOrAdmin]
    filter_backends = (filters.DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter)
    filterset_class = ServiceRequestFilter
    search_fields = ['pet_type', 'pet_breed', 'location', 'description']
    ordering_fields = ['start_date', 'end_date', 'created_at', 'location']
    

    def get_queryset(self):
        user = self.request.user
        if user.is_staff or user.user_type =="caregiver":
            return ServiceRequest.objects.all()
        return ServiceRequest.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.owner != request.user and not request.user.is_staff:
            return Response({"detail": "You do not have permission to delete this service request."},
                            status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
        
class ServiceOffersFilter(filters.FilterSet):
    service_request = filters.NumberFilter(field_name='service_request__id')
    caregiver = filters.NumberFilter(field_name='caregiver__id')

    class Meta:
        model = ServiceOffer
        fields = ['service_request', 'caregiver']

class ServiceOfferViewSet(viewsets.ModelViewSet):
    queryset = ServiceOffer.objects.all()
    serializer_class = ServiceOfferSerializer
    permission_classes = [IsCaregiverOrReadOnlyOrAdmin]
    filterset_class = ServiceOffersFilter


    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return ServiceOffer.objects.all()
        elif user.user_type == "caregiver":
            return ServiceOffer.objects.filter(caregiver=user)
        else:
            return ServiceOffer.objects.filter(service_request__owner=user)

    def create(self, request, *args, **kwargs):
        service_request_id = request.data.get('service_request')
        existing_offer = ServiceOffer.objects.filter(
            service_request_id=service_request_id,
            caregiver=request.user
        ).first()

        if existing_offer:
            if existing_offer.status == 'rejected':
                # If the existing offer was rejected, update it instead of creating a new one
                serializer = self.get_serializer(existing_offer, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                return Response(serializer.data)
            else:
                return Response({"detail": "You have already made an offer for this request."}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.caregiver != request.user:
            return Response({"detail": "You can only update your own offers."}, status=status.HTTP_403_FORBIDDEN)
        if instance.status not in ['pending', 'rejected']:
            return Response({"detail": "You can only update pending or rejected offers."}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(caregiver=self.request.user, status='pending')

    def perform_update(self, serializer):
        serializer.save(status='pending')
        

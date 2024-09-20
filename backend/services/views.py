from django_filters import rest_framework as filters
from rest_framework import viewsets, permissions
from rest_framework import filters as drf_filters
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
        

class ServiceOfferViewSet(viewsets.ModelViewSet):
    queryset = ServiceOffer.objects.all()
    serializer_class = ServiceOfferSerializer
    permission_classes = [IsCaregiverOrReadOnlyOrAdmin]

    def get_queryset(self):
        """
        This view should return:
        - All offers for admins
        - Own offers for caregivers
        - Offers for owned service requests for other users
        """
        user = self.request.user
        if user.is_staff:
            return ServiceOffer.objects.all()
        elif user.user_type =="caregiver":
            return ServiceOffer.objects.filter(caregiver=user)
        else:
            return ServiceOffer.objects.filter(service_request__owner=user)

    def perform_create(self, serializer):
        serializer.save(caregiver=self.request.user)
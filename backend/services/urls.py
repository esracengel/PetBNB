from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceRequestViewSet, ServiceOfferViewSet

router = DefaultRouter()
router.register(r'service-requests', ServiceRequestViewSet, basename='servicerequest')
router.register(r'service-offers', ServiceOfferViewSet, basename = 'serviceoffer')

urlpatterns = [
    path('', include(router.urls)),
]
from django.urls import path, include
from rest_framework_simplejwt.views import TokenBlacklistView

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include('djoser.urls.jwt')),
    path('jwt/destroy/', TokenBlacklistView.as_view(), name='jwt-destroy'),
]
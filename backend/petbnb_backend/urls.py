
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users/', include('users.urls')),
    path('auth/', include('users.urls')),
    path('services/', include('services.urls')),
    path('reviews/', include('reviews.urls')),
    path('messages/', include('messaging.urls')),
]

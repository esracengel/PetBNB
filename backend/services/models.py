from django.db import models
from django.conf import settings

class ServiceRequest(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    pet_type = models.CharField(max_length=50)
    pet_breed = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.pet_type} care request by {self.owner.username}"
    
    
class ServiceOffer(models.Model):
    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='offers')
    caregiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_offers')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    message = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('request_inactive', 'Request Inactive')
    ], default='pending')

    class Meta:
        unique_together = ('service_request', 'caregiver')

    def __str__(self):
        return f"Offer by {self.caregiver.user.username} for {self.service_request}"

    def save(self, *args, **kwargs):
        if self.caregiver.user_type != "caregiver":
            raise ValueError("Only caregivers can make service offers.")
        if not self.service_request.is_active:
            self.status = 'request_inactive'
        super().save(*args, **kwargs)
    
    
class Service(models.Model):
    service_request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name = 'service')
    accepted_offer = models.OneToOneField(ServiceOffer, on_delete=models.CASCADE, related_name = 'service')
    date_accepted = models.DateTimeField(auto_now_add=True)
    has_happened = models.BooleanField(default=False)
    
    @property
    def pet_owner(self):
        """
        Returns the User object of the pet owner associated with this service.
        
        :return: User object
        :rtype: User
        """
        return self.service_request.owner
    
    @property
    def caregiver(self):
        """
        Returns the User object of the caregiver associated with this service.
        
        :return: User object
        :rtype: User
        """
        return self.accepted_offer.caregiver
    
    def __str__(self):
        return f"Service provided by {self.accepted_offer.caregiver} for {self.service_request.owner}."
    
    def is_user_involved(self, user):
        
        """
        Checks if the given user is involved in this service (either as pet owner or caregiver).
        
        :param user: The user to check
        :type user: User
        :return: True if the user is involved, False otherwise
        :rtype: bool
        """
        return user == self.pet_owner or user == self.caregiver
    
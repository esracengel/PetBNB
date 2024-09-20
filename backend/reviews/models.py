from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from services.models import Service


class Review(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name ='reviews')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_giver')
    reviewee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_receiver')
    rating =models.IntegerField(validators = [MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['service', 'reviewer']
        
    def __str__(self):
        return f"Review by {self.reviewer} for {self.reviewee}"
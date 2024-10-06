from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('staff', 'Staff'),
        ('petowner', 'Pet Owner'),
        ('caregiver', 'Caregiver'),
    )
    
    email = models.EmailField(unique=True, null = False, blank = False)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, null = False, blank = False, default = "petowner")
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    district = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'user_type']

    def __str__(self):
        return self.email
    
    def clean(self):
        super().clean()
        if not self.email:
            raise ValidationError(_('The Email field must be set'))
        
    @property
    def display_name(self):
        return self.username or self.email.split('@')[0]
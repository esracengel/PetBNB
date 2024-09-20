from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from reviews.models import Review
from services.models import Service, ServiceRequest, ServiceOffer
from datetime import date

User = get_user_model()

class ReviewViewSetTest(TestCase):
    def setUp(self):
        # Create users, service request, service offer, and service for testing
        self.client = APIClient()
        
        self.pet_owner = User.objects.create_user(username='pet_owner', email='owner@example.com', password='testpass123', user_type='petowner')
        self.caregiver = User.objects.create_user(username='caregiver', email='caregiver@example.com', password='testpass123', user_type='caregiver')
        self.other_user = User.objects.create_user(username='other_user', email='other@example.com', password='testpass123', user_type='petowner')
        
        self.service_request = ServiceRequest.objects.create(
            owner=self.pet_owner,
            start_date=date(2024, 8, 1),
            end_date=date(2024, 8, 5),
            pet_type='Dog',
            pet_breed='Labrador',
            location='New York',
            description='Need dog sitting'
        )
        
        self.service_offer = ServiceOffer.objects.create(
            service_request=self.service_request,
            caregiver=self.caregiver,
            price=50.00,
            message='I can take care of your dog'
        )
        
        self.service = Service.objects.create(
            service_request=self.service_request,
            accepted_offer=self.service_offer
        )
        
        self.review_data = {
            'service': self.service.id,
            'reviewee': self.caregiver.id,
            'rating': 5,
            'comment': 'Great service!'
        }
        
        self.url = reverse('review-list')

    def test_create_review_as_pet_owner(self):
        # Test creating a review as the pet owner
        self.client.force_authenticate(user=self.pet_owner)
        response = self.client.post(self.url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.get().reviewer, self.pet_owner)

    def test_create_review_as_caregiver(self):
        # Test creating a review as the caregiver
        self.client.force_authenticate(user=self.caregiver)
        review_data = self.review_data.copy()
        review_data['reviewee'] = self.pet_owner.id
        response = self.client.post(self.url, review_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(Review.objects.get().reviewer, self.caregiver)

    def test_create_review_as_uninvolved_user(self):
        # Test that an uninvolved user can't create a review
        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(self.url, self.review_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), 0)

    def test_list_reviews(self):
        # Test that users can only see reviews they're involved in
        Review.objects.create(
            service=self.service,
            reviewer=self.pet_owner,
            reviewee=self.caregiver,
            rating=5,
            comment='Great service!'
        )
        Review.objects.create(
            service=self.service,
            reviewer=self.caregiver,
            reviewee=self.pet_owner,
            rating=4,
            comment='Good pet owner'
        )
        
        # Test pet owner can see both reviews
        self.client.force_authenticate(user=self.pet_owner)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Test other user can't see any reviews
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_update_own_review(self):
        # Test that a user can update their own review
        review = Review.objects.create(
            service=self.service,
            reviewer=self.pet_owner,
            reviewee=self.caregiver,
            rating=4,
            comment='Good service'
        )
        self.client.force_authenticate(user=self.pet_owner)
        url = reverse('review-detail', kwargs={'pk': review.id})
        response = self.client.patch(url, {'rating': 5, 'comment': 'Great service!'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        review.refresh_from_db()
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great service!')

    def test_update_others_review(self):
        # Test that a user can't update someone else's review
        review = Review.objects.create(
            service=self.service,
            reviewer=self.pet_owner,
            reviewee=self.caregiver,
            rating=4,
            comment='Good service'
        )
        self.client.force_authenticate(user=self.caregiver)
        url = reverse('review-detail', kwargs={'pk': review.id})
        response = self.client.patch(url, {'rating': 3, 'comment': 'Not so good'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        review.refresh_from_db()
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, 'Good service')

    def test_delete_review(self):
        # Test that a user can delete their own review
        review = Review.objects.create(
            service=self.service,
            reviewer=self.pet_owner,
            reviewee=self.caregiver,
            rating=4,
            comment='Good service'
        )
        self.client.force_authenticate(user=self.pet_owner)
        url = reverse('review-detail', kwargs={'pk': review.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Review.objects.count(), 0)
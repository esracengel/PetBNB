from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from reviews.models import Review
from services.models import Service, ServiceRequest, ServiceOffer
from datetime import date

User = get_user_model()

class ReviewModelTest(TestCase):
    def setUp(self):
        # Create users, service request, service offer, and service for testing
        self.pet_owner = User.objects.create_user(username='pet_owner', email='owner@example.com', password='testpass123', user_type='petowner')
        self.caregiver = User.objects.create_user(username='caregiver', email='caregiver@example.com', password='testpass123', user_type='caregiver')
        
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

    def test_review_creation(self):
        # Test creating a review with valid data
        review = Review.objects.create(
            service=self.service,
            reviewer=self.pet_owner,
            reviewee=self.caregiver,
            rating=5,
            comment='Great service!'
        )
        self.assertIsInstance(review, Review)
        self.assertEqual(review.service, self.service)
        self.assertEqual(review.reviewer, self.pet_owner)
        self.assertEqual(review.reviewee, self.caregiver)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great service!')

    def test_review_str_representation(self):
        # Test the string representation of a Review object
        review = Review.objects.create(
            service=self.service,
            reviewer=self.pet_owner,
            reviewee=self.caregiver,
            rating=4,
            comment='Good job'
        )
        expected_str = f"Review by {self.pet_owner} for {self.caregiver}"
        self.assertEqual(str(review), expected_str)

    def test_review_rating_constraints(self):
        # Test that ratings below 1 and above 5 are not allowed
        # Test rating below minimum
        with self.assertRaises(ValidationError):
            review = Review(
                service=self.service,
                reviewer=self.pet_owner,
                reviewee=self.caregiver,
                rating=0,
                comment='Invalid rating'
            )
            review.full_clean()

        # Test rating above maximum
        with self.assertRaises(ValidationError):
            review = Review(
                service=self.service,
                reviewer=self.pet_owner,
                reviewee=self.caregiver,
                rating=6,
                comment='Invalid rating'
            )
            review.full_clean()

    def test_unique_review_per_service_and_reviewer(self):
        # Test that a user can't review the same service twice
        Review.objects.create(
            service=self.service,
            reviewer=self.pet_owner,
            reviewee=self.caregiver,
            rating=5,
            comment='First review'
        )
        
        with self.assertRaises(ValidationError):
            duplicate_review = Review(
                service=self.service,
                reviewer=self.pet_owner,
                reviewee=self.caregiver,
                rating=4,
                comment='Duplicate review'
            )
            duplicate_review.full_clean()
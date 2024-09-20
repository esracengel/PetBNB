from django.shortcuts import render
from django.db.models import Q
from rest_framework import viewsets
from .models import Review
from .serializers import ReviewSerializer
from .permissions import CanCreateReview

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [CanCreateReview]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)

    def get_queryset(self):
        return Review.objects.filter(Q(reviewer=self.request.user) | Q(reviewee=self.request.user))
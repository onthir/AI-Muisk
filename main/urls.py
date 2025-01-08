from django.urls import path
from .views import RecommendationView, RecommendationDetailView, MusicRecommenderAI

urlpatterns = [
    path("recommendations/", RecommendationView.as_view(), name="recommendations"),
    path("recommendations/<int:pk>/", RecommendationDetailView.as_view(), name="recommendation_detail"),
    path("recommender/", MusicRecommenderAI.as_view(), name="recommender"),
]

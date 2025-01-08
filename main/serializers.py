from rest_framework import serializers
from .models import Recommendations, Links, Themes

class RecommendationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendations
        fields = '__all__'


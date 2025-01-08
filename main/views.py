from django.shortcuts import render
from rest_framework.views import APIView
from .models import Recommendations, Links, Themes
from .serializers import RecommendationsSerializer
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import google.generativeai as genai
from django.conf import settings
import json
# Create your views here.

class RecommendationView(APIView):
    # get method
    def get(self, request):
        recommendations = Recommendations.objects.all()
        serializer = RecommendationsSerializer(recommendations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = RecommendationsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# put, delete, details

class RecommendationDetailView(APIView):
    def get(self, request, pk):
        recommendation = get_object_or_404(Recommendations, pk=pk)
        serializer = RecommendationsSerializer(recommendation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    # put request
    def put(self, request, pk):
        recommendation = get_object_or_404(Recommendations, pk=pk)
        serializer = RecommendationsSerializer(recommendation, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # delete request
    def delete(self, request, pk):
        recommendation = get_object_or_404(Recommendations, pk=pk)
        recommendation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# recommender bot
class MusicRecommenderAI(APIView):
    def post(self, request):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        user_query = request.data.get('query', '')
        
        
        instructions = """
        You are a music recommendation assistant. Based on the user query, your task is to recommend 5 songs that fit the query's mood, genre, or theme. For each song, generate a JSON object containing the following keys:

name: Title of the song.
artist: The main artist or band performing the song.
album: The album the song belongs to.
release_date: The song's release date in YYYY-MM-DD format.
themes: A list of themes or moods the song conveys (e.g., love, nostalgia, empowerment, sadness).
album_art: URL to the album cover image.
links: An array containing URLs where the song can be listened to explicitly: Spotify, Apple Music, YouTube.
        Please don't include '```json' in the result. just provide the object
        """

        prompt = f"""
        {instructions}    

        User Query: {user_query}    
"""
        response = model.generate_content(prompt)
        json_response = ""
# Try to parse the response text as JSON
        try:
            json_response = json.loads(response.text)  # Parse response into Python object
            print(json.dumps(json_response, indent=4))  # Pretty-print the JSON
        except json.JSONDecodeError as e:
            print("Failed to decode JSON:", e)
            print("Raw response:", response.text)

        # create entry in database
        save_recommendations_from_json(json_response)
        return Response({'response': json_response}, status=status.HTTP_200_OK)
    

# a method to save the json response into datbase

def save_recommendations_from_json(json_response):
    # extract the list
    # recommendations = json_response.get('response', [])
    # print("REcommendations: ", recommendations)
    for rec in json_response:

        theme_objects = []
        # themes
        for theme in rec.get("themes", []):
            theme_obj, _= Themes.objects.get_or_create(name=theme)
            theme_objects.append(theme_obj)

        # create recommendation
        recommendation = Recommendations.objects.create(
            name=rec.get("name", ""),
            artist=rec.get("artist", ""),
            album=rec.get("album", ""),
            release_date=rec.get("release_date", ""),
            album_art=rec.get("album_art", "")
        )

        recommendation.save()

        recommendation.themes.set(theme_objects)

        # save links
        links_data = rec.get("links", [])
        try:
            Links.objects.create(
                recommendation=recommendation,
                youtube_link=links_data[2],
                spotify_link=links_data[0],
                applie_music_link=links_data[1]
            )
        except:
            print("Error adding links")


        print("Successfully added to the database")

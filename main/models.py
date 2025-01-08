from django.db import models



class Themes(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Recommendations(models.Model):
    name = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    album = models.CharField(max_length=100)
    release_date = models.DateField()
    themes = models.ManyToManyField(Themes, max_length=100, null=True, blank=True)
    album_art = models.URLField(max_length=500)


    def __str__(self):
        return self.name



    
class Links(models.Model):
    recommendation = models.ForeignKey(Recommendations, on_delete=models.CASCADE)
    youtube_link = models.URLField(max_length=500)
    spotify_link = models.URLField(max_length=500)
    applie_music_link = models.URLField(max_length=500)

    def __str__(self):
        return self.recommendation.name
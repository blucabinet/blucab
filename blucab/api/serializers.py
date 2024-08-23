from rest_framework import serializers
from main.models import Movie


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            "ean",
            "asin",
            "title",
            "title_clean",
            "format",
            "release_year",
            "runtime",
            "fsk",
            "content",
            "actor",
            "regisseur",
            "studio",
            "genre",
            "language",
            "disc_count",
            "movie_count",
            "season_count",
            "episode_count",
            "is_series",
            "picture_available",
        ]

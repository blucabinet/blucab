from rest_framework import serializers
from main.models import Movie
from django.templatetags.static import static


class MovieSerializer(serializers.ModelSerializer):

    picture_url = serializers.SerializerMethodField("assembled_url")

    def assembled_url(self, Movie):

        if Movie.picture_available:
            file_path = "main/cover/"
            file_name = Movie.ean
        else:
            file_path = "main/"
            file_name = "dummy"

        path = file_path + file_name + ".jpg"
        url = static(path)
        return url

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
            "picture_url",
        ]

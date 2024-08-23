from rest_framework import serializers
from main.models import Movie, MovieUserList, UserSettings
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


class MovieUserListSerializer(serializers.ModelSerializer):

    movie_title_clean = serializers.SerializerMethodField("title_clean")
    movie_format = serializers.SerializerMethodField("format")
    user_name = serializers.SerializerMethodField("username")

    def title_clean(self, MovieUserList):
        return MovieUserList.movie.title_clean

    def format(self, MovieUserList):
        return MovieUserList.movie.format
    
    def username(self, MovieUserList):
        return MovieUserList.user.username

    class Meta:
        model = MovieUserList
        fields = [
            "user_name",
            "movie",
            "movie_title_clean",
            "movie_format",
            "activated",
            "rating",
            "viewed",
            "rented",
            "rented_to",
            "date_added",
            "price",
        ]

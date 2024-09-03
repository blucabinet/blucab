from rest_framework import serializers
from main.models import User, Movie, MovieUserList, UserSettings
from django.templatetags.static import static
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data["username"], None, validated_data["password"]
        )
        return user


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Invalid Details.")


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


class UserSettingsSerializer(serializers.ModelSerializer):

    user_name = serializers.SerializerMethodField("username")

    def username(self, UserSettings):
        return UserSettings.user.username

    class Meta:
        model = UserSettings
        fields = [
            "user_name",
            "price_unit",
            "days_for_new",
            "view_is_public",
            "show_view_title",
            "show_view_details",
            "show_view_icon_new",
            "show_view_icon_rented",
            "show_view_count_disc",
            "show_view_count_movie",
            "show_view_button_details",
        ]

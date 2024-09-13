from rest_framework import status, serializers
import rest_framework.exceptions as exceptions
from main.models import User, Movie, MovieUserList, UserSettings
from django.templatetags.static import static
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email")


class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")
        extra_kwargs = {
            "username": {"required": True},
            "email": {"required": True},
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


class MovieUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MovieUserList
        fields = ("user", "movie")


class CreateMovieUserSerializer(serializers.ModelSerializer):
    ean = serializers.CharField()

    class Meta:
        model = MovieUserList
        fields = ("user", "ean")
        extra_kwargs = {
            "ean": {"required": True},
        }

    def create(self, validated_data):
        user_v = validated_data["user"]
        ean_v = validated_data["ean"]

        if not Movie.objects.filter(ean=ean_v).exists():
            raise exceptions.NotFound(detail="Movie not in Database")

        movie_v = Movie.objects.get(ean=ean_v)

        if not MovieUserList.objects.filter(user=user_v, movie=movie_v).exists():
            item = MovieUserList.objects.create(
                user=user_v,
                movie=Movie.objects.get(ean=ean_v),
            )
            return item
        else:
            raise exceptions.NotAcceptable(detail="Entry already exists")


class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(style={"input_type": "password"})

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise exceptions.AuthenticationFailed()


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

    user_name = serializers.SerializerMethodField("_username")
    movie_title_clean = serializers.SerializerMethodField("_title_clean")
    movie_format = serializers.SerializerMethodField("_format")
    movie_picture_url = serializers.SerializerMethodField("_picture_url")
    movie_picture_available = serializers.SerializerMethodField("_picture_available")
    movie_disc_count = serializers.SerializerMethodField("_disc_count")
    movie_count = serializers.SerializerMethodField("_movie_count")
    movie_is_series = serializers.SerializerMethodField("_is_series")
    movie_runtime = serializers.SerializerMethodField("_runtime")
    movie_ean = serializers.SerializerMethodField("_ean")
    movie_fsk = serializers.SerializerMethodField("_fsk")

    def _picture_url(self, MovieUserList):

        if MovieUserList.movie.picture_available:
            file_path = "main/cover/"
            file_name = MovieUserList.movie.ean
        else:
            file_path = "main/"
            file_name = "dummy"

        path = file_path + file_name + ".jpg"
        url = static(path)
        return url

    def _title_clean(self, MovieUserList):
        return MovieUserList.movie.title_clean

    def _format(self, MovieUserList):
        return MovieUserList.movie.format

    def _username(self, MovieUserList):
        return MovieUserList.user.username

    def _picture_available(self, MovieUserList):
        return MovieUserList.movie.picture_available

    def _disc_count(self, MovieUserList):
        return MovieUserList.movie.disc_count

    def _movie_count(self, MovieUserList):
        return MovieUserList.movie.movie_count

    def _is_series(self, MovieUserList):
        return MovieUserList.movie.is_series

    def _runtime(self, MovieUserList):
        return MovieUserList.movie.runtime

    def _ean(self, MovieUserList):
        return MovieUserList.movie.ean

    def _fsk(self, MovieUserList):
        return MovieUserList.movie.fsk

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
            "movie_picture_available",
            "movie_picture_url",
            "movie_disc_count",
            "movie_count",
            "movie_is_series",
            "movie_runtime",
            "movie_ean",
            "movie_fsk",
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

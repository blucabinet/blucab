from django import forms
from .models import UserSettings, MovieUserList, Movie


class UpdateUserSettings(forms.ModelForm):
    class Meta:
        model = UserSettings
        fields = [
            "view_is_public",
            "show_view_title",
            "show_view_icon_rented",
            "show_view_icon_new",
            "show_view_button_share",
            "show_view_button_details",
            "show_view_details",
            "show_view_count_disc",
            "show_view_count_movie",
            "days_for_new",
            "price_unit",
        ]
        exclude = ["user"]


class UpdateMovie(forms.ModelForm):
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
            "fsk_nbr",
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
            "is_bluray_uhd",
            "picture_available",
            "picture_url_original",
            "picture_url_original_hd",
            "picture_processed",
            "needs_parsing",
            "imdb_id",
        ]


class UpdateMovieUserList(forms.ModelForm):
    class Meta:
        model = MovieUserList
        fields = [
            "activated",
            "rating",
            "viewed",
            "rented",
            "rented_to",
            "date_added",
            "price",
        ]
        exclude = [
            "user",
            "movie",
        ]

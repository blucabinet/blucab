from django import forms
from .models import UserSettings, MovieUserList


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

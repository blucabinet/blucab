from django import forms
from .models import UserSettings


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

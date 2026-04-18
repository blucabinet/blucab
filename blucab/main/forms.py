from django import forms
from .models import UserCabinet, UserSettings, MovieUserList, Movie
from django.utils.translation import gettext as _


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
            "archived",
            "rating",
            "viewed",
            "rented",
            "rented_to",
            "date_added",
            "price",
            "url_custom",
            "url_name",
            "cabinet",
        ]
        exclude = [
            "user",
            "movie",
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields["cabinet"].queryset = UserCabinet.objects.filter(user=user)


class CabinetAddForm(forms.ModelForm):
    class Meta:
        model = UserCabinet
        fields = ["name"]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": _("e.g. Living Room Cabinet"),
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get("name")

        if UserCabinet.objects.filter(user=self.user, name=name).exists():
            raise forms.ValidationError(_("You already have a cabinet with this name."))

        return name


class CabinetDeleteForm(forms.Form):
    cabinet = forms.ModelChoiceField(
        queryset=UserCabinet.objects.none(),
        label=_("Cabinet to delete"),
        empty_label=_("--- Choose a cabinet ---"),
        widget=forms.Select(attrs={"class": "form-select"})
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['cabinet'].queryset = UserCabinet.objects.filter(user=self.user)

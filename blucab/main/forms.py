from django import forms
from .models import UserCabinet, UserSettings, MovieUserList, Movie, MovieErrorReport
from django.utils.translation import gettext_lazy as _


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
            "activated",
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
            "languages",
            "disc_count",
            "movie_count",
            "season_count",
            "episode_count",
            "is_series",
            "is_bluray_uhd",
            "is_bluray_3d",
            "picture_available",
            "picture_url_original",
            "picture_url_original_hd",
            "picture_processed",
            "force_picture_disable",
            "needs_parsing",
            "imdb_id",
            "flickrack_id",
            "date_added",
            "date_updated",
        ]
        widgets = {
            "date_added": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "date_updated": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "price": forms.NumberInput(attrs={"type": "number", "step": "0.01"}),
            "picture_url_original": forms.TextInput(attrs={"type": "url"}),
            "picture_url_original_hd": forms.TextInput(attrs={"type": "url"}),
            "content": forms.Textarea(attrs={"rows": 5}),
            "languages": forms.SelectMultiple(
                attrs={
                    "class": "select2-multiple",
                    "data-placeholder": _("Choose Languages..."),
                    "style": "width: 100%;",
                }
            ),
        }


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
            "rented_since",
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
        widgets = {
            "rating": forms.NumberInput(
                attrs={"type": "range", "min": "0", "max": "6", "step": "1"}
            ),
            "rented_since": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "date_added": forms.DateInput(format="%Y-%m-%d", attrs={"type": "date"}),
            "price": forms.NumberInput(attrs={"type": "number", "step": "0.01"}),
            "url_custom": forms.TextInput(attrs={"type": "url"}),
        }

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
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields["cabinet"].queryset = UserCabinet.objects.filter(user=self.user)


class AddMovieForm(forms.Form):
    query = forms.CharField(
        max_length=128,
        label=_("EAN or Title"),
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": _("Enter EAN or search term"),
            }
        ),
    )


class MovieErrorReportForm(forms.ModelForm):
    class Meta:
        model = MovieErrorReport
        fields = ["picture_wrong", "content_wrong", "wrong_ean_asin", "comment"]
        widgets = {
            "comment": forms.Textarea(attrs={"rows": 3}),
        }

from django.conf import settings
from main.models import Movie, MovieUserList
from .amazon import contentParser

import csv
import os
import requests


PICTURE_EXTENSION = ".jpg"
CSV_ENCODING = "ISO-8859-1"


class handler:

    def __init__(self):
        pass

    def _check_int_string(self, input: str) -> int:
        if input == "":
            return 0
        else:
            return int(input)

    def _picture_download(self, url: str, name: str) -> None:
        picture_name = name + PICTURE_EXTENSION
        file_path = os.path.join(
            settings.BASE_DIR, "main", "static", "main", "cover", picture_name
        )

        if not os.path.exists(file_path):
            picture = requests.get(url)
            open(file_path, "wb").write(picture.content)
            print(f"File {picture_name} downloaded")

        return

    def csv_importer(self, filename: str, user) -> None:
        with open(
            os.path.join(settings.BASE_DIR, "import", filename), encoding=CSV_ENCODING
        ) as csv_file:
            reader = csv.reader(csv_file, delimiter=",")
            next(reader, None)  # Skip CSV header
            for row in reader:
                csv_ean = row[1]
                csv_rating = self._check_int_string(row[13])

                if not Movie.objects.filter(ean=csv_ean).exists():
                    m = Movie(
                        ean=csv_ean,
                        asin=row[2],
                        title=row[3],
                        title_clean=row[4],
                        format=row[5],
                        release_year=self._check_int_string(row[6]),
                        runtime=self._check_int_string(row[7]),
                        fsk=row[8],
                        content=row[9],
                        actor=row[10],
                        regisseur=row[11],
                        studio=row[12],
                    )

                    m.save()

                db_movie = Movie.objects.get(ean=csv_ean)

                if not MovieUserList.objects.filter(user=user, movie=db_movie).exists():
                    list_item = MovieUserList(
                        user=user,
                        movie=db_movie,
                        rating=csv_rating,
                    )
                    list_item.save()

        return

    def add_movie(self, ean: str) -> bool:
        pars = contentParser(ean, item_limit=1)

        if len(pars.soups) > 0:
            soup = pars.soups[0]
            pars_picture_url = pars.get_image(soup)
            pars_picture_available = False

            if pars_picture_url != None:
                pars_picture_available = True

            if not Movie.objects.filter(ean=ean).exists():
                m = Movie(
                    ean=ean,
                    asin=pars.get_asin(soup),
                    title=pars.get_title(soup),
                    title_clean=pars.get_title_clean(soup),
                    format=pars.get_format(soup),
                    release_year=pars.get_release_year(soup),
                    runtime=pars.get_runtime_min(soup),
                    fsk=pars.get_fsk_str(soup),
                    fsk_nbr=pars.get_fsk(soup),
                    content=pars.get_content(soup),
                    actor=pars.get_actors(soup),
                    regisseur=pars.get_regisseur(soup),
                    studio=pars.get_studio(soup),
                    genre=pars.get_genre(soup),
                    language=pars.get_language(soup),
                    disc_count=pars.get_disc_count(soup),
                    picture_available=pars_picture_available,
                    picture_url_original=pars_picture_url,
                    needs_parsing=False,
                )

                m.save()

                self._picture_download(pars_picture_url, ean)

                return True

        return False

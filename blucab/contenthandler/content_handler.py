from django.conf import settings
from main.models import Movie, MovieUserList
from .amazon import contentParser
from .picture_helper import pictureHelper as ph

import csv
import os
import time
import random

CSV_ENCODING = "ISO-8859-1"


class handler:

    def __init__(self):
        pass

    def _check_int_string(self, input: str) -> int:
        if input == "":
            return None
        else:
            return int(input)

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

    def add_new_movie(self, ean: str) -> bool:
        pars = contentParser(ean, item_limit=1)

        if len(pars.soups) > 0:
            soup = pars.soups[0]
            pars_picture_url = pars.get_image_url(soup)
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
                    picture_processed=pars_picture_available,
                    needs_parsing=False,
                )

                m.save()

                ph.picture_download(pars_picture_url, ean)
                ph.picture_postprocessing(ean)

                return True

        return False

    def check_all_picture_available(self) -> None:
        movies = Movie.objects.filter(picture_available=True)

        for movie in movies:
            exists = ph._picture_exists(movie.ean)
            movie.picture_available = exists
            if not exists:
                movie.picture_processed = False
            movie.save()
        return

    def picture_update(self) -> None:
        movies = Movie.objects.filter(picture_available=True, picture_processed=False)

        for movie in movies:
            ph.picture_postprocessing(movie.ean)
            movie.picture_processed = True
            movie.save()
        return

    def get_missing_information(self) -> None:
        movies = Movie.objects.filter(needs_parsing=True)
        counter = 0

        for movie in movies:
            if counter == 10:
                return
            counter = counter + 1

            # Slow down speed for parsing
            t = random.randint(2, 10)
            time.sleep(t)

            movie_ean = movie.ean
            pars = contentParser(movie_ean, item_limit=1)

            if len(pars.soups) == 0:
                print("ContentParser failed!")
                continue

            soup = pars.soups[0]

            if movie.release_year == None:
                movie.release_year = pars.get_release_year(soup)

            if movie.runtime == None:
                movie.runtime = pars.get_runtime_min(soup)

            if movie.fsk == None:
                movie.fsk = pars.get_fsk_str(soup)

            if movie.fsk_nbr == None:
                movie.fsk_nbr = pars.get_fsk(soup)

            if movie.content == None:
                movie.content = pars.get_content(soup)

            if movie.actor == None:
                movie.actor = pars.get_actors(soup)

            if movie.regisseur == None:
                movie.regisseur = pars.get_regisseur(soup)

            if movie.studio == None:
                movie.studio = pars.get_studio(soup)

            if movie.genre == None:
                movie.genre = pars.get_genre(soup)

            if movie.language == None:
                movie.language = pars.get_language(soup)

            if movie.disc_count == 1:
                count = pars.get_disc_count(soup)
                if count != None:
                    movie.disc_count = count

            # Picture update
            pars_picture_url = pars.get_image_url(soup)

            if movie.picture_url_original_hd == None:
                movie.picture_url_original_hd = pars.get_image_url(soup, use_hd=True)

            if (pars_picture_url != None) and (movie.picture_available == False):
                ph.picture_download(pars_picture_url, movie_ean)
                ph.picture_postprocessing(movie_ean)
                movie.picture_url_original = pars_picture_url
                movie.picture_available = True
                movie.picture_processed = True

            movie.needs_parsing = False
            movie.save()
        return

    def content_update(self) -> None:
        self.check_all_picture_available()
        self.get_missing_information()
        self.picture_update()
        return

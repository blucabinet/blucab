from django.conf import settings
from django.http import HttpResponse
from main.models import Movie, MovieUserList
from .amazon import contentParser, PRODUCT_DESCRIPTION_ITEMS
from .picture_helper import pictureHelper

import csv
import os
import time
import random

CSV_ENCODING_UTF8 = "utf-8"
CSV_ENCODING_FLICKRACK = "ISO-8859-1"
CSV_ENCODING_BLUCAB = CSV_ENCODING_UTF8

IDENTIFIER_FLICKRACK = b'Position,EAN,ASIN,Titel,Titel ohne Zusatz,Format,Release,Laufzeit,FSK,Inhalt,Schauspieler,Regisseur/e,Studio,Bewertung\n' #['Position', 'EAN', 'ASIN', 'Titel', 'Titel ohne Zusatz', 'Format', 'Release', 'Laufzeit', 'FSK', 'Inhalt', 'Schauspieler', 'Regisseur/e', 'Studio', 'Bewertung']
IDENTIFIER_BLUCAB = b'movie,activated,rating,viewed,rented,rented_to,date_added,price,ean,asin,title,title_clean,format,release_year,runtime,fsk,fsk_nbr,content,actor,regisseur,studio,genre,language,disc_count,movie_count,season_count,episode_count,is_series,is_bluray_uhd,picture_url_original,picture_url_original_hd,imdb_id\r\n' #['movie', 'activated', 'rating', 'viewed', 'rented', 'rented_to', 'date_added', 'price', 'ean', 'asin', 'title', 'title_clean', 'format', 'release_year', 'runtime', 'fsk', 'fsk_nbr', 'content', 'actor', 'regisseur', 'studio', 'genre', 'language', 'disc_count', 'movie_count', 'season_count', 'episode_count', 'is_series', 'is_bluray_uhd', 'picture_url_original', 'picture_url_original_hd', 'imdb_id']

ph = pictureHelper()


class handler:

    def __init__(self):
        pass

    def _check_int_string(self, input: str) -> int:
        if input == "":
            return None
        else:
            return int(input)

    def _check_bool_string(self, input: str) -> bool:
        if input == "":
            return None
        else:
            return bool(input)

    def _check_string(self, input: str) -> str:
        if input == "":
            return None
        else:
            return str(input)

    def csv_importer(self, filename: str, user) -> bool:
        with open(
            os.path.join(settings.BASE_DIR, "import", filename), mode="rb"
        ) as file:
            header = file.readline()
            file.close()

            if header == IDENTIFIER_FLICKRACK:
                with open(
                    os.path.join(settings.BASE_DIR, "import", filename),
                    encoding=CSV_ENCODING_FLICKRACK,
                ) as csv_file:
                    reader = csv.reader(csv_file, delimiter=",")
                    header = next(reader, None)

                    for row in reader:
                        csv_ean = row[1]
                        csv_rating = self._check_int_string(row[13])

                        if not Movie.objects.filter(ean=csv_ean).exists():
                            m = Movie(
                                ean=csv_ean,
                                asin=self._check_string(row[2]),
                                title=self._check_string(row[3]),
                                title_clean=self._check_string(row[4]),
                                format=self._check_string(row[5]),
                                release_year=self._check_int_string(row[6]),
                                runtime=self._check_int_string(row[7]),
                                fsk=self._check_string(row[8]),
                                fsk_nbr=None,
                                content=self._check_string(row[9]),
                                actor=self._check_string(row[10]),
                                regisseur=self._check_string(row[11]),
                                studio=self._check_string(row[12]),
                                needs_parsing=True,
                            )

                            m.save()

                        db_movie = Movie.objects.get(ean=csv_ean)

                        if not MovieUserList.objects.filter(
                            user=user, movie=db_movie
                        ).exists():
                            list_item = MovieUserList(
                                user=user,
                                movie=db_movie,
                                rating=csv_rating,
                            )
                            list_item.save()

                    return True
            if header == IDENTIFIER_BLUCAB:
                with open(
                    os.path.join(settings.BASE_DIR, "import", filename),
                    encoding=CSV_ENCODING_BLUCAB,
                ) as csv_file:
                    reader = csv.reader(csv_file, delimiter=",")
                    header = next(reader, None)

                    for row in reader:
                        csv_ean = row[8]
                        csv_activated = self._check_bool_string(row[1])
                        csv_rating = self._check_int_string(row[2])
                        csv_viewed = self._check_bool_string(row[3])
                        csv_rented = self._check_bool_string(row[4])
                        csv_rented_to = self._check_string(row[5])
                        csv_date_added = self._check_string(row[6])
                        csv_price = self._check_string(row[7])

                        if not Movie.objects.filter(ean=csv_ean).exists():
                            m = Movie(
                                ean=csv_ean,
                                asin=self._check_string(row[9]),
                                title=self._check_string(row[10]),
                                title_clean=self._check_string(row[11]),
                                format=self._check_string(row[12]),
                                release_year=self._check_int_string(row[13]),
                                runtime=self._check_int_string(row[14]),
                                fsk=self._check_string(row[15]),
                                fsk_nbr=self._check_int_string(row[16]),
                                content=self._check_string(row[17]),
                                actor=self._check_string(row[18]),
                                regisseur=self._check_string(row[19]),
                                studio=self._check_string(row[20]),
                                genre=self._check_string(row[21]),
                                language=self._check_string(row[22]),
                                disc_count=self._check_int_string(row[23]),
                                movie_count=self._check_int_string(row[24]),
                                season_count=self._check_int_string(row[25]),
                                episode_count=self._check_int_string(row[26]),
                                is_series=self._check_bool_string(row[27]),
                                is_bluray_uhd=self._check_bool_string(row[28]),
                                picture_url_original=self._check_string(row[29]),
                                picture_url_original_hd=self._check_string(row[30]),
                                imdb_id=self._check_string(row[31]),
                                needs_parsing=False,
                            )

                            m.save()

                        db_movie = Movie.objects.get(ean=csv_ean)

                        if not MovieUserList.objects.filter(
                            user=user, movie=db_movie
                        ).exists():
                            list_item = MovieUserList(
                                user=user,
                                movie=db_movie,
                                activated=csv_activated,
                                rating=csv_rating,
                                viewed=csv_viewed,
                                rented=csv_rented,
                                rented_to=csv_rented_to,
                                date_added=csv_date_added,
                                price=csv_price,
                            )
                            list_item.save()

                    return True
            else:
                # CSV Format not known
                return False

    def csv_exporter(self, user) -> HttpResponse:
        queryset = MovieUserList.objects.filter(user=user)
        opts_mul = queryset.model._meta
        opts_ml = Movie.objects.model._meta

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = "attachment;filename=export.csv"

        writer = csv.writer(response)
        field_names_mul = [field.name for field in opts_mul.fields]
        field_names_ml = [field.name for field in opts_ml.fields]

        remove_items = {
            "id",
            "user",
            "needs_parsing",
            "picture_processed",
            "picture_available",
        }
        for item in remove_items:
            try:
                field_names_mul.remove(item)
            except:
                pass
            try:
                field_names_ml.remove(item)
            except:
                pass

        # Write the csv header
        writer.writerow(field_names_mul + field_names_ml)

        for obj in queryset:
            row_mul = [getattr(obj, field) for field in field_names_mul]
            row_ml = [getattr(obj.movie, field) for field in field_names_ml]

            writer.writerow(row_mul + row_ml)

        return response

    def add_new_movie(self, ean: str) -> bool:
        pars = contentParser(ean, item_limit=1)

        if len(pars.soups) > 0:
            soup = pars.soups[0]
            pars_picture_url = pars.get_image_url(soup)
            pars_picture_url_hd = pars.get_image_url(soup, use_hd=True)
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
                    is_bluray_uhd=pars.is_bluray_uhd(soup),
                    picture_available=pars_picture_available,
                    picture_url_original=pars_picture_url,
                    picture_url_original_hd=pars_picture_url_hd,
                    picture_processed=pars_picture_available,
                    needs_parsing=False,
                )

                m.save()

                if pars_picture_available:
                    ph.picture_download_processing(pars_picture_url, ean)

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
        movies_img_unavailable = Movie.objects.filter(
            picture_available=False, picture_processed=False
        )

        for movie in movies_img_unavailable:
            if movie.picture_url_original != None:
                ph.picture_download_processing(movie.picture_url_original, movie.ean)
                movie.picture_available = True
                movie.picture_processed = True
                movie.save()

        movies_img_available = Movie.objects.filter(
            picture_available=True, picture_processed=False
        )

        for movie in movies_img_available:
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
                print(
                    f"ContentParser failed! Movie: {movie.title}, EAN: {movie_ean}, ASIN: {movie.asin}"
                )
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
            else:
                for item in PRODUCT_DESCRIPTION_ITEMS:
                    movie.content = movie.content.replace(item, "").lstrip()

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

            if movie.is_bluray_uhd == False:
                movie.is_bluray_uhd = pars.is_bluray_uhd(soup)

            # Picture update
            pars_picture_url = pars.get_image_url(soup)

            if movie.picture_url_original_hd == None:
                movie.picture_url_original_hd = pars.get_image_url(soup, use_hd=True)

            if (pars_picture_url != None) and (movie.picture_available == False):
                ph.picture_download_processing(pars_picture_url, movie_ean)
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

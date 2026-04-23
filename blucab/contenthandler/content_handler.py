from django.conf import settings
from django.http import HttpResponse
from main.models import Movie, MovieUserList
from .amazon import contentParser, PRODUCT_DESCRIPTION_ITEMS, AMAZON_STR_FSK_NO
from .picture_helper import pictureHelper, PICTURE_NAME_PROCESSED_SD

import csv
import os
import time
import random
import re

CSV_ENCODING_UTF8 = "utf-8"
CSV_ENCODING_FLICKRACK = "ISO-8859-1"
CSV_ENCODING_BLUCAB = CSV_ENCODING_UTF8

IDENTIFIER_FLICKRACK = b'Position,EAN,ASIN,Titel,Titel ohne Zusatz,Format,Release,Laufzeit,FSK,Inhalt,Schauspieler,Regisseur/e,Studio,Bewertung\n' #['Position', 'EAN', 'ASIN', 'Titel', 'Titel ohne Zusatz', 'Format', 'Release', 'Laufzeit', 'FSK', 'Inhalt', 'Schauspieler', 'Regisseur/e', 'Studio', 'Bewertung']
IDENTIFIER_BLUCAB = b'movie,activated,rating,viewed,rented,rented_to,date_added,price,ean,asin,title,title_clean,format,release_year,runtime,fsk,fsk_nbr,content,actor,regisseur,studio,genre,language,disc_count,movie_count,season_count,episode_count,is_series,is_bluray_uhd,picture_url_original,picture_url_original_hd,imdb_id\r\n' #['movie', 'activated', 'rating', 'viewed', 'rented', 'rented_to', 'date_added', 'price', 'ean', 'asin', 'title', 'title_clean', 'format', 'release_year', 'runtime', 'fsk', 'fsk_nbr', 'content', 'actor', 'regisseur', 'studio', 'genre', 'language', 'disc_count', 'movie_count', 'season_count', 'episode_count', 'is_series', 'is_bluray_uhd', 'picture_url_original', 'picture_url_original_hd', 'imdb_id']

ph = pictureHelper()


class handler:

    def __init__(self):
        pass

    def _check_int_string(self, input: str, default=None) -> int:
        if not input or str(input).strip() == "":
            return default

        try:
            return int(float(input))
        except (ValueError, TypeError):
            return default

    def _check_bool_string(self, input: str, default=False) -> bool:
        if not input or str(input).strip() == "":
            return default

        value = str(input).strip().lower()
        if value in ["true", "1", "t", "y", "yes"]:
            return True
        if value in ["false", "0", "f", "n", "no"]:
            return False
        return default

    def _check_string(self, input: str, default=None) -> str:
        if not input or str(input).strip() == "":
            return default

        return str(input).strip()

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
                    reader = csv.DictReader(csv_file, delimiter=",")

                    for row in reader:
                        csv_ean = row["EAN"]
                        csv_rating = self._check_int_string(row["Bewertung"])
                        csv_fsk_nbr = row["FSK"]

                        try:
                            fsk_nbr = re.findall(r"\b\d+\b", csv_fsk_nbr)[0]
                        except:
                            if csv_fsk_nbr == AMAZON_STR_FSK_NO:
                                fsk_nbr = 0
                            else:
                                fsk_nbr = None

                        if not Movie.objects.filter(ean=csv_ean).exists():
                            m = Movie(
                                ean=csv_ean,
                                asin=self._check_string(row.get("ASIN")),
                                title=self._check_string(row.get("Titel")),
                                title_clean=self._check_string(row.get("Titel ohne Zusatz")),
                                format=self._check_string(row.get("Format")),
                                release_year=self._check_int_string(row.get("Release")),
                                runtime=self._check_int_string(row.get("Laufzeit")),
                                fsk=csv_fsk_nbr,
                                fsk_nbr=fsk_nbr,
                                content=self._check_string(row.get("Inhalt")),
                                actor=self._check_string(row.get("Schauspieler")),
                                regisseur=self._check_string(row.get("Regisseur/e")),
                                studio=self._check_string(row.get("Studio")),
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
                    reader = csv.DictReader(csv_file, delimiter=",")

                    for row in reader:
                        csv_ean = row["ean"]
                        csv_activated = self._check_bool_string(row.get("activated"))
                        csv_rating = self._check_int_string(row.get("rating"))
                        csv_viewed = self._check_bool_string(row.get("viewed"))
                        csv_rented = self._check_bool_string(row.get("rented"))
                        csv_rented_to = self._check_string(row.get("rented_to"))
                        csv_date_added = self._check_string(row.get("date_added"))
                        csv_price = self._check_string(row.get("price"))
                        csv_archived = self._check_bool_string(row.get("archived"))

                        if not Movie.objects.filter(ean=csv_ean).exists():
                            m = Movie(
                                ean=csv_ean,
                                asin=self._check_string(row.get("asin")),
                                title=self._check_string(row.get("title")),
                                title_clean=self._check_string(row.get("title_clean")),
                                format=self._check_string(row.get("format")),
                                release_year=self._check_int_string(row.get("release_year")),
                                runtime=self._check_int_string(row.get("runtime")),
                                fsk=self._check_string(row.get("fsk")),
                                fsk_nbr=self._check_int_string(row.get("fsk_nbr")),
                                content=self._check_string(row.get("content")),
                                actor=self._check_string(row.get("actor")),
                                regisseur=self._check_string(row.get("regisseur")),
                                studio=self._check_string(row.get("studio")),
                                genre=self._check_string(row.get("genre")),
                                language=self._check_string(row.get("language")),
                                disc_count=self._check_int_string(row.get("disc_count")),
                                movie_count=self._check_int_string(row.get("movie_count")),
                                season_count=self._check_int_string(row.get("season_count")),
                                episode_count=self._check_int_string(row.get("episode_count")),
                                is_series=self._check_bool_string(row.get("is_series")),
                                is_bluray_uhd=self._check_bool_string(row.get("is_bluray_uhd")),
                                picture_url_original=self._check_string(row.get("picture_url_original")),
                                picture_url_original_hd=self._check_string(row.get("picture_url_original_hd")),
                                imdb_id=self._check_string(row.get("imdb_id")),
                                needs_parsing=False,
                            )

                            m.save()

                        db_movie = Movie.objects.get(ean=csv_ean)

                        list_item, created = MovieUserList.objects.update_or_create(
                            user=user, 
                            movie=db_movie,
                            
                            defaults={
                                'activated': csv_activated,
                                'rating': csv_rating,
                                'viewed': csv_viewed,
                                'rented': csv_rented,
                                'rented_to': csv_rented_to,
                                'date_added': csv_date_added,
                                'price': csv_price,
                                'archived': csv_archived,
                            }
                        )

                        print(f"{'Erstellt' if created else 'Aktualisiert'}: {db_movie.title}")

                    return True
            else:
                # CSV Format not known
                return False
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
        # Only check for SD pictures right now.
        movies = Movie.objects.filter()

        for movie in movies:
            exists = ph._picture_exists(
                folder=movie.ean, picture=PICTURE_NAME_PROCESSED_SD
            )
            movie.picture_available = exists
            if not exists:
                movie.picture_processed = False
            movie.save()
        return

    def picture_update(self) -> None:
        # Only update SD pictures right now.
        movies_img_unavailable = Movie.objects.filter(
            picture_available=False, picture_processed=False
        )

        for movie in movies_img_unavailable:
            if movie.picture_url_original != None:
                ph.picture_download_processing(
                    url=movie.picture_url_original, ean=movie.ean, is_hd=False
                )
                movie.picture_available = True
                movie.picture_processed = True
                movie.save()

        movies_img_available = Movie.objects.filter(
            picture_available=True, picture_processed=False
        )

        for movie in movies_img_available:
            ph.picture_postprocessing(folder=movie.ean)
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

from django.conf import settings
from .models import Movie, MovieUserList

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

    def csv_importer(self, filename: str, user):
        with open(
            os.path.join(settings.BASE_DIR, "import", filename), encoding=CSV_ENCODING
        ) as csv_file:
            reader = csv.reader(csv_file, delimiter=",")
            next(reader, None) #Skip CSV header
            for row in reader:
                csv_ean = row[1]

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
                    list_item = MovieUserList(user=user, movie=db_movie)
                    list_item.save()

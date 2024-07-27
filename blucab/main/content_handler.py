from django.conf import settings
from .models import Movie

import csv
import os
import requests


PICTURE_EXTENSION = ".jpg"
CSV_ENCODING = "ISO-8859-1"


class handler():

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
            settings.BASE_DIR, "main", "static", "main", picture_name
        )
        picture = requests.get(url)

        if not os.path.exists(file_path):
            open(file_path, "wb").write(picture.content)
            print(f"File {picture_name} downloaded")

    def csv_importer(self, filename: str):
        with open(os.path.join(settings.BASE_DIR, "import", filename), encoding=CSV_ENCODING) as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            next(reader, None)
            for row in reader:
                c_ean = row[1]

                if not Movie.objects.filter(ean=c_ean).exists():
                    m = Movie(
                        ean=c_ean,
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

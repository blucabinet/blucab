from django.conf import settings

import os
import requests

from PIL import Image, ImageChops

PICTURE_EXTENSION = ".jpg"
MINIMUM_IMAGE_HEIGHT = 50


class pictureHelper:

    def __init__(self):
        pass

    def __picture_file_path(self, name: str) -> str:
        picture_name = name + PICTURE_EXTENSION
        return os.path.join(
            settings.BASE_DIR, "main", "static", "main", "cover", picture_name
        )

    def _picture_exists(self, name) -> bool:
        file_path = self.__picture_file_path(name)
        return os.path.exists(file_path)

    def picture_postprocessing(self, name: str) -> None:
        def trim(im):
            bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
            diff = ImageChops.difference(im, bg)
            diff = ImageChops.add(diff, diff, 2.0, -100)
            bbox = diff.getbbox()
            if bbox:
                return im.crop(bbox)
            else:
                # Failed to find the borders, convert to "RGB"
                return trim(im.convert("RGB"))

        if self._picture_exists(name):
            im = Image.open(self.__picture_file_path(name))

            if im.height > MINIMUM_IMAGE_HEIGHT:
                im.save(
                    self.__picture_file_path(f"orig_{name}")
                )  # ToDo: Maybe remove in future
                im = trim(im)
                im.save(self.__picture_file_path(name))
        return

    def picture_download(self, url: str, name: str) -> None:
        file_path = self.__picture_file_path(name)

        if not self._picture_exists(file_path):
            picture = requests.get(url)
            open(file_path, "wb").write(picture.content)
            print(f"File {file_path} downloaded")
        return

    def picture_download_processing(self, url: str, name: str) -> None:
        self.picture_download(url, name)
        self.picture_postprocessing(name)
        return

from django.conf import settings

import os
import requests

from PIL import Image, ImageChops

PICTURE_EXTENSION = ".jpg"
PICTURE_NAME_PROCESSED_SD = "cover"
PICTURE_NAME_PROCESSED_HD = "cover_hd"
PICTURE_NAME_RAW_SD = "cover_sd_raw"
PICTURE_NAME_RAW_HD = "cover_hd_raw"

MINIMUM_IMAGE_HEIGHT = 50


class pictureHelper:

    def __init__(self):
        pass

    def __picture_file_path(
        self,
        folder: str,
        picture: str = PICTURE_NAME_PROCESSED_SD,
        extension: str = PICTURE_EXTENSION,
    ) -> str:
        folder_name = folder
        picture_name = picture + extension
        return os.path.join(
            settings.BASE_DIR,
            "main",
            "static",
            "main",
            "cover",
            folder_name,
            picture_name,
        )

    def _picture_exists(
        self,
        folder: str,
        picture: str = PICTURE_NAME_PROCESSED_SD,
        extension: str = PICTURE_EXTENSION,
    ) -> bool:
        file_path = self.__picture_file_path(folder, picture, extension)
        return os.path.exists(file_path)

    def picture_postprocessing(self, folder: str) -> None:
        def trim(im):
            bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
            diff = ImageChops.difference(im, bg)
            diff = ImageChops.add(diff, diff, 2.0, -100)
            bbox = diff.getbbox()
            if bbox:
                return im.crop(bbox)

            if im.mode != "RGB":
                # Failed to find the borders, convert to "RGB" and try again.
                return trim(im.convert("RGB"))

            return im

        if not self._picture_exists(folder=folder, picture=PICTURE_NAME_RAW_SD):
            return

        raw_path = self.__picture_file_path(folder=folder, picture=PICTURE_NAME_RAW_SD)
        processed_path = self.__picture_file_path(
            folder=folder, picture=PICTURE_NAME_PROCESSED_SD
        )

        with Image.open(raw_path) as im:
            if im.height > MINIMUM_IMAGE_HEIGHT:
                trim_im = trim(im)
                trim_im.save(processed_path)

        return

    def picture_download(self, url: str, ean: str, is_hd: bool = False) -> None:
        # Only check for SD pictures right now.
        file_path = self.__picture_file_path(folder=ean, picture=PICTURE_NAME_RAW_SD)

        if not self._picture_exists(folder=ean, picture=PICTURE_NAME_RAW_SD):
            picture = requests.get(url)

            directory = os.path.dirname(file_path)
            os.makedirs(directory, exist_ok=True)

            with open(file_path, "wb") as f:
                f.write(picture.content)

        return

    def picture_download_processing(
        self, url: str, ean: str, is_hd: bool = False
    ) -> None:
        self.picture_download(url=url, ean=ean, is_hd=is_hd)
        self.picture_postprocessing(folder=ean)

        return

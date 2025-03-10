from bs4 import BeautifulSoup
import requests
import re

AMAZON_BASE_URL = "https://www.amazon.de"
AMAZON_ASIN = "ASIN"
AMAZON_STR_FSK = "Alterseinstufung"
AMAZON_STR_FSK_NO = "Freigegeben ohne Altersbeschränkung"
AMAZON_STR_REGISSEUR = "Regisseur"
AMAZON_STR_MEDIAFORMAT = "Medienformat"
AMAZON_STR_DISKS = "Anzahl Disks"
AMAZON_STR_ACTOR = "Darsteller"
AMAZON_STR_SUBTITLE = "Untertitel"
AMAZON_STR_LANGUAGE = "Sprache"
AMAZON_STR_STUDIO = "Studio"
AMAZON_STR_RUNTIME = "Laufzeit"
AMAZON_STR_RELEASE = "Erscheinungstermin"
AMAZON_STR_HOUR = "Stunde"
AMAZON_STR_HOURS = "Stunden"
AMAZON_STR_MINUTES = "Minuten"
AMAZON_STR_AND = "und"
AMAZON_STR_PICTURE_SD = "src"
AMAZON_STR_PICTURE_HD = "data-old-hires"

FORMAT_BLURAY = "Blu-Ray"
FORMAT_DVD = "DVD"

UHD_STR = "4K"

REMOVE_ITEMS = {
    "[Blu-ray]",
    "Blu ray",
    "Blu-ray",
    "Blu-Ray",
    "[Blu-ray 2D]",
    "[4K Ultra HD]",
    "(4K Ultra-HD)",
    "4K-UHD",
    "4K UHD",
    "UHD",
    "[DVD]",
    "(Fanedition)",
    "[Limited Edition]",
    "(Remastered)",
    "(OmU)",
    "(Special Edition)",
    "[]",
    "()",
}

BLURAY_ITEMS = {
    "[Blu-ray]",
    "Blu ray",
    "Blu-ray",
    "Blu-Ray",
    "[Blu-ray 2D]",
    "[4K Ultra HD]",
    "(4K Ultra-HD)",
    "4K-UHD",
    "4K UHD",
}

BLURAY_UHD_ITEMS = {
    "Blu-ray 4K"
    "4K Ultra HD",
    "4K Ultra-HD",
    "4K-UHD",
    "4K UHD",
    "UHD",
    "BR4K",
}

DVD_ITEMS = {
    "[DVD]",
    "DVD",
    "dvd",
}

PRODUCT_DESCRIPTION_ITEMS = {
    "Product Description:",
    "Produktbeschreibung:",
    "Kurzbeschreibung:",
    "Besonderheiten:",
    "Amazon.de:",
}


class contentParser:

    # Headers for request
    HEADERS = {
        "User-Agent": "Mozilla/6.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
        "Accept-Language": "de",
    }

    def __init__(self, search_term, item_limit=1):
        self.search_link_list = []
        self.soups = []

        # The webpage URL for searches
        URL = AMAZON_BASE_URL + "/s?k=" + search_term + "&ref=nb_sb_noss"

        # HTTP Request
        webpage = requests.get(URL, headers=self.HEADERS)

        if webpage.status_code != 200:
            print(f"An parsing error occurred with status {webpage.status_code}")
            return

        # Soup Object containing all data
        soup = BeautifulSoup(webpage.content, "lxml")

        # Fetch links as List of Tag Objects
        links = soup.find_all("a", attrs={"class": "a-link-normal s-no-outline"})

        # Loop for extracting links from Tag Objects
        for link in links:
            self.search_link_list.append(link.get("href"))

        for i in range(len(self.search_link_list)):
            new_webpage = requests.get(
                AMAZON_BASE_URL + self.search_link_list[i], headers=self.HEADERS
            )

            self.soups.append(BeautifulSoup(new_webpage.content, "lxml"))

            if i == item_limit - 1:
                break

        return

    def _get_str_numbers(self, string):
        return re.findall(r"\b\d+\b", string)

    def get_product_information(self, soup, searchtext: str) -> str:
        try:
            feature = soup.find("div", attrs={"id": "detailBullets_feature_div"})

            list = feature.find_all("li")

            for item in list:
                list_entry = item.find("span", attrs={"class": "a-list-item"})

                if str(list_entry).find(searchtext) != -1:
                    str_processed = (
                        str(list_entry)
                        .replace(
                            '<span class="a-list-item"> <span class="a-text-bold">', ""
                        )
                        .replace("</span> <span>", "")
                        .replace("</span> </span>", "")
                        .replace(searchtext, "")
                        .replace(":", "", 1)
                        .replace("\r", "")
                        .replace("\n", "")
                        .replace("\u200e", "")
                        .replace("\u200f", "")
                        .removeprefix(", ")
                        .lstrip()
                        .strip()
                    )

                    # Remove multiple whitespaces
                    str_processed = re.sub(" +", " ", str_processed)

                    return str_processed

            list_entry = None

        except AttributeError:
            list_entry = None

        return list_entry

    def get_asin(self, soup) -> str:
        return self.get_product_information(soup, AMAZON_ASIN)

    def get_image_url(self, soup, use_hd=False) -> str:

        if use_hd:
            type = AMAZON_STR_PICTURE_HD
        else:
            type = AMAZON_STR_PICTURE_SD

        try:
            img = soup.find("div", attrs={"id": "imgTagWrapperId"}).find("img")
            img_url = img[type].strip()

            if img_url == "":
                img_url = None

        except AttributeError:
            img_url = None

        return img_url

    def get_genre(self, soup) -> str:

        try:
            genre = soup.find("tr", attrs={"class": "a-spacing-small po-genre"}).find(
                "span", attrs={"class": "a-size-base po-break-word"}
            )
            genre_value = genre.text

            genre_string = genre_value.strip()

        except AttributeError:
            genre_string = None

        return genre_string

    def get_title(self, soup) -> str:

        try:
            title = soup.find("span", attrs={"id": "productTitle"})

            title_value = title.string

            title_string = title_value.strip()

        except AttributeError:
            title_string = None

        return title_string

    def get_content(self, soup) -> str:

        try:
            content = soup.find("div", attrs={"id": "productDescription"})
            content_string = content.text.strip()

            for item in PRODUCT_DESCRIPTION_ITEMS:
                content_string = content_string.replace(item, "").lstrip()

        except AttributeError:
            content_string = None

        return content_string

    def get_title_clean(self, soup) -> str:
        title = self.get_title(soup)

        for item in REMOVE_ITEMS:
            title = title.replace(item, "")

        return title.strip()

    def get_format(self, soup) -> str:
        input = self.get_title(soup)

        for item in BLURAY_ITEMS:
            if item in input:
                return FORMAT_BLURAY

        for item in DVD_ITEMS:
            if item in input:
                return FORMAT_DVD

        return None

    def is_bluray_uhd(self, soup) -> bool:
        title = self.get_title(soup)

        try:
            if UHD_STR in self.get_mediaformat(soup):
                return True

            for item in BLURAY_UHD_ITEMS:
                if item in title:
                    return True

            return False
        except:
            return False

    def get_fsk_str(self, soup) -> str:
        return self.get_product_information(soup, AMAZON_STR_FSK)

    def get_fsk(self, soup) -> int:
        fsk = self.get_fsk_str(soup)

        try:
            number = self._get_str_numbers(fsk)[0]

        except:
            if fsk == AMAZON_STR_FSK_NO:
                number = 0
            else:
                number = None

        return number

    def get_regisseur(self, soup) -> str:
        return self.get_product_information(soup, AMAZON_STR_REGISSEUR)

    def get_mediaformat(self, soup) -> str:
        return self.get_product_information(soup, AMAZON_STR_MEDIAFORMAT)

    def get_disc_count(self, soup) -> str:
        return self.get_product_information(soup, AMAZON_STR_DISKS)

    def get_actors(self, soup) -> str:
        return self.get_product_information(soup, AMAZON_STR_ACTOR)

    def get_subtitle(self, soup) -> str:
        return self.get_product_information(soup, AMAZON_STR_SUBTITLE)

    def get_language(self, soup) -> str:
        return self.get_product_information(soup, AMAZON_STR_LANGUAGE)

    def get_studio(self, soup) -> str:
        return self.get_product_information(soup, AMAZON_STR_STUDIO)

    def get_runtime_str(self, soup) -> str:
        return self.get_product_information(soup, AMAZON_STR_RUNTIME)

    def get_runtime_min(self, soup) -> int:
        rtime = self.get_runtime_str(soup)

        try:
            str_count_hour = rtime.count(AMAZON_STR_HOUR) + rtime.count(AMAZON_STR_HOURS)
            str_count_minutes = rtime.count(AMAZON_STR_MINUTES)

            time = self._get_str_numbers(rtime)

            if (str_count_hour >= 1) and (str_count_minutes >= 1):
                hours = time[0]
                minutes = time[1]

                total_minutes = int(hours) * 60 + int(minutes)

            if (str_count_hour == 0) and (str_count_minutes >= 1):
                minutes = time[0]
                total_minutes = int(minutes)

            if (str_count_hour >= 1) and (str_count_minutes == 0):
                hours = time[0]

                total_minutes = int(hours) * 60

        except:
            total_minutes = None

        return total_minutes

    def get_release_year_str(self, soup) -> str:
        return self.get_product_information(soup, AMAZON_STR_RELEASE)

    def get_release_year(self, soup) -> str:
        ryear = self.get_release_year_str(soup)

        try:
            ryear = str(ryear).strip().split(" ")

            if len(ryear[2]) == 4:
                year = ryear[2]
            else:
                year = None
        except:
            year = None

        return year


if __name__ == "__main__":

    ean = "Star Wars Blu-Ray"
    # ean = "B0DF5PYLT7"
    # ean = "4010232053060"
    # ean = "4010232066398"

    pars = contentParser(ean, item_limit=1)

    for soup in pars.soups:
        # Function calls to display all necessary product information
        print("ASIN =", pars.get_asin(soup))
        print("Format =", pars.get_format(soup))
        print("Genre =", pars.get_genre(soup))
        print("Product Title =", pars.get_title(soup))
        print("Stripped Title =", pars.get_title_clean(soup))
        print("ImageUrl =", pars.get_image_url(soup))
        print("FSK (str) =", pars.get_fsk_str(soup))
        print("FSK (nbr) =", pars.get_fsk(soup))
        print("Regisseur =", pars.get_regisseur(soup))
        print("Disc-Count =", pars.get_disc_count(soup))
        print("Darsteller =", pars.get_actors(soup))
        print("Untertitel =", pars.get_subtitle(soup))
        print("Sprache =", pars.get_language(soup))
        print("Studio =", pars.get_studio(soup))
        print("Laufzeit (str) =", pars.get_runtime_str(soup))
        print("Laufzeit (min) =", pars.get_runtime_min(soup))
        print("Release (str) =", pars.get_release_year_str(soup))
        print("Release (year) =", pars.get_release_year(soup))
        # print("Content =", pars.get_content(soup))
        print()

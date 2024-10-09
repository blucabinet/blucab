from bs4 import BeautifulSoup
import requests
import re

AMAZON_BASE_URL = "https://www.amazon.de"
AMAZON_ASIN = "ASIN"
AMAZON_STR_FSK = "Alterseinstufung"
AMAZON_STR_FSK_NO = "Freigegeben ohne Altersbeschränkung"
AMAZON_STR_REGISSEUR = "Regisseur"
AMAZON_STR_DISKS = "Anzahl Disks"
AMAZON_STR_ACTOR = "Darsteller"
AMAZON_STR_SUBTITLE = "Untertitel"
AMAZON_STR_LANGUAGE = "Sprache"
AMAZON_STR_STUDIO = "Studio"
AMAZON_STR_RUNTIME = "Laufzeit"
AMAZON_STR_RELEASE = "Erscheinungstermin"
AMAZON_STR_HOUR = "Stunden"
AMAZON_STR_MINUTES = "Minuten"
AMAZON_STR_AND = "und"

FORMAT_BLURAY = "Blu-Ray"
FORMAT_DVD = "DVD"

REMOVE_ITEMS = {
    "[Blu-ray]",
    "Blu ray",
    "Blu-ray",
    "Blu-Ray",
    "[Blu-ray 2D]",
    "[4k Ultra HD]",
    "[DVD]",
    "(Fanedition)",
    "[Limited Edition]",
    "(Remastered)",
    "(OmU)",
    "(Special Edition)",
    "[]",
}

BLURAY_ITEMS = {
    "[Blu-ray]",
    "Blu ray",
    "Blu-ray",
    "Blu-Ray",
    "[Blu-ray 2D]",
    "[4k Ultra HD]",
}

DVD_ITEMS = {
    "[DVD]",
    "DVD",
    "dvd",
}


class contentParser:

    # Headers for request
    HEADERS = {
        "User-Agent": "Mozilla/6.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
        "Accept-Language": "de",
    }

    search_link_list = []

    def __init__(self, search_term):
        # The webpage URL for searches
        URL = AMAZON_BASE_URL + "/s?k=" + search_term + "&ref=nb_sb_noss"

        # HTTP Request
        webpage = requests.get(URL, headers=self.HEADERS)

        # Soup Object containing all data
        soup = BeautifulSoup(webpage.content, "lxml")

        # Fetch links as List of Tag Objects
        links = soup.find_all("a", attrs={"class": "a-link-normal s-no-outline"})

        # Loop for extracting links from Tag Objects
        for link in links:
            self.search_link_list.append(link.get("href"))

        return

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

    def get_asin(self, url) -> str:
        return self.get_product_information(soup, AMAZON_ASIN)
        # try:
        #    asin_string = url.split("/dp/")[1].split("/")[0]

    #
    # except AttributeError:
    #    asin_string = ""
    #
    # return asin_string

    def get_image(self, soup) -> str:

        try:
            img = soup.find("div", attrs={"id": "imgTagWrapperId"}).find("img")
            img_url = img["src"].strip()

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
            if str(input).find(item) != -1:
                return FORMAT_BLURAY

        for item in DVD_ITEMS:
            if str(input).find(item) != -1:
                return FORMAT_DVD

        return None

    def get_fsk_str(self, soup) -> str:
        return self.get_product_information(soup, AMAZON_STR_FSK)

    def get_fsk(self, soup) -> int:
        fsk = self.get_fsk_str(soup)

        try:
            numbers = re.findall(r"\b\d+\b", fsk)
            number = numbers[0]

        except:
            if fsk == AMAZON_STR_FSK_NO:
                number = 0
            else:
                number = None

        return number

    def get_regisseur(self, soup) -> str:
        return self.get_product_information(soup, AMAZON_STR_REGISSEUR)

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

    def get_runtime_min(self, soup) -> str:
        rtime = self.get_runtime_str(soup)

        try:
            time = (
                str(rtime)
                .replace(AMAZON_STR_HOUR, "")
                .replace(AMAZON_STR_MINUTES, "")
                .replace(" ", "")
                .split(AMAZON_STR_AND)
            )

            hours = time[0]
            minutes = time[1]

            total_minutes = int(hours) * 60 + int(minutes)

            # ToDo: Error-Handling if not in hours and only minutes.

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

    pars = contentParser("4010232053060")

    # Loop for extracting product details from each link
    # for link in links_list:
    for link in pars.search_link_list:

        new_webpage = requests.get(AMAZON_BASE_URL + link, headers=pars.HEADERS)

        new_soup = BeautifulSoup(new_webpage.content, "lxml")

        # Function calls to display all necessary product information
        print("ASIN =", pars.get_asin(new_webpage.url))
        print("Format =", pars.get_format(new_soup))
        print("Genre =", pars.get_genre(new_soup))
        print("Product Title =", pars.get_title(new_soup))
        print("Stripped Title =", pars.get_title_clean(new_soup))
        print("ImageUrl =", pars.get_image(new_soup))
        print("FSK (str) =", pars.get_fsk_str(new_soup))
        print("FSK (nbr) =", pars.get_fsk(new_soup))
        print("Regisseur =", pars.get_regisseur(new_soup))
        print("Disc-Count =", pars.get_disc_count(new_soup))
        print("Darsteller =", pars.get_actors(new_soup))
        print("Untertitel =", pars.get_subtitle(new_soup))
        print("Sprache =", pars.get_language(new_soup))
        print("Studio =", pars.get_studio(new_soup))
        print("Laufzeit (str) =", pars.get_runtime_str(new_soup))
        print("Laufzeit (min) =", pars.get_runtime_min(new_soup))
        print("Release (str) =", pars.get_release_year_str(new_soup))
        print("Release (year) =", pars.get_release_year(new_soup))
        print("Content =", pars.get_content(new_soup))
        print()

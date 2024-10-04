from bs4 import BeautifulSoup
import requests
import re

AMAZON_BASE_URL = "https://www.amazon.de"
AMAZON_STR_FSK = "Alterseinstufung"
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
    "Blu-Ray",
    "[Blu-ray 2D]",
    "[4k Ultra HD]",
    "[DVD]",
    "(Fanedition)",
    "[Limited Edition]",
    "(Remastered)",
    "(OmU)",
    "(Special Edition)",
}

BLURAY_ITEMS = {
    "[Blu-ray]",
    "Blu ray",
    "[Blu-ray 2D]",
    "[4k Ultra HD]",
}

DVD_ITEMS = {
    "[DVD]",
    "DVD",
    "dvd",
}


def get_product_information(soup, searchtext: str) -> str:
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

        list_entry = ""

    except AttributeError:
        list_entry = ""

    return list_entry


def get_asin(url) -> str:

    try:
        asin_string = url.split("/dp/")[1].split("/")[0]

    except AttributeError:
        asin_string = ""

    return asin_string


def get_image(soup) -> str:

    try:
        img = soup.find("div", attrs={"id": "imgTagWrapperId"}).find("img")
        img_url = img["src"].strip()

    except AttributeError:
        img_url = ""

    return img_url


def get_genre(soup) -> str:

    try:
        genre = soup.find("tr", attrs={"class": "a-spacing-small po-genre"}).find(
            "span", attrs={"class": "a-size-base po-break-word"}
        )
        genre_value = genre.text

        genre_string = genre_value.strip()

    except AttributeError:
        genre_string = ""

    return genre_string


def get_title(soup) -> str:

    try:
        title = soup.find("span", attrs={"id": "productTitle"})

        title_value = title.string

        title_string = title_value.strip()

    except AttributeError:
        title_string = ""

    return title_string


def get_content(soup) -> str:

    try:
        content = soup.find("div", attrs={"id": "productDescription"})
        content_string = content.text

    except AttributeError:
        content_string = ""

    return content_string


def get_title_clean(soup) -> str:
    title = get_title(soup)

    for item in REMOVE_ITEMS:
        title = title.replace(item, "")

    return title.strip()


def get_format(soup) -> str:
    input = get_title(soup)

    for item in BLURAY_ITEMS:
        if str(input).find(item) != -1:
            return FORMAT_BLURAY

    for item in DVD_ITEMS:
        if str(input).find(item) != -1:
            return FORMAT_DVD

    return ""


def get_fsk_str(soup) -> str:
    return get_product_information(soup, AMAZON_STR_FSK)


def get_fsk(soup) -> int:
    fsk = get_fsk_str(soup)

    # ToDo: do processing

    return fsk


def get_regisseur(soup) -> str:
    return get_product_information(soup, AMAZON_STR_REGISSEUR)


def get_disc_count(soup) -> str:
    return get_product_information(soup, AMAZON_STR_DISKS)


def get_actors(soup) -> str:
    return get_product_information(soup, AMAZON_STR_ACTOR)


def get_subtitle(soup) -> str:
    return get_product_information(soup, AMAZON_STR_SUBTITLE)


def get_language(soup) -> str:
    return get_product_information(soup, AMAZON_STR_LANGUAGE)


def get_studio(soup) -> str:
    return get_product_information(soup, AMAZON_STR_STUDIO)


def get_runtime_str(soup) -> str:
    return get_product_information(soup, AMAZON_STR_RUNTIME)


def get_runtime_min(soup) -> str:
    rtime = get_runtime_str(soup)

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

    return total_minutes


def get_release_year_str(soup) -> str:
    return get_product_information(soup, AMAZON_STR_RELEASE)


def get_release_year(soup) -> str:
    ryear = get_release_year_str(soup)

    ryear = str(ryear).strip().split(" ")

    if len(ryear[2]) == 4:
        year = ryear[2]
    else:
        year = 0

    return year


if __name__ == "__main__":

    # Headers for request
    HEADERS = {
        "User-Agent": "Mozilla/6.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
        "Accept-Language": "de",
    }

    # The webpage URL for searches
    URL = AMAZON_BASE_URL + "/s?k=4010232053060&ref=nb_sb_noss"

    # HTTP Request
    webpage = requests.get(URL, headers=HEADERS)

    # Soup Object containing all data
    soup = BeautifulSoup(webpage.content, "lxml")

    # Fetch links as List of Tag Objects
    links = soup.find_all("a", attrs={"class": "a-link-normal s-no-outline"})

    # Store the links
    links_list = []

    # Loop for extracting links from Tag Objects
    for link in links:
        links_list.append(link.get("href"))

    # Loop for extracting product details from each link
    # for link in links_list:
    for link in links_list:

        new_webpage = requests.get(AMAZON_BASE_URL + link, headers=HEADERS)

        new_soup = BeautifulSoup(new_webpage.content, "lxml")

        # Function calls to display all necessary product information
        print("ASIN =", get_asin(new_webpage.url))
        print("Format =", get_format(new_soup))
        print("Genre =", get_genre(new_soup))
        print("Product Title =", get_title(new_soup))
        print("Stripped Title =", get_title_clean(new_soup))
        print("ImageUrl =", get_image(new_soup))
        print("FSK =", get_fsk(new_soup))
        print("Regisseur =", get_regisseur(new_soup))
        print("Disc-Count =", get_disc_count(new_soup))
        print("Darsteller =", get_actors(new_soup))
        print("Untertitel =", get_subtitle(new_soup))
        print("Sprache =", get_language(new_soup))
        print("Studio =", get_studio(new_soup))
        print("Laufzeit (str) =", get_runtime_str(new_soup))
        print("Laufzeit (min) =", get_runtime_min(new_soup))
        print("Release (str) =", get_release_year_str(new_soup))
        print("Release (year) =", get_release_year(new_soup))
        print("Content =", get_content(new_soup))
        print()

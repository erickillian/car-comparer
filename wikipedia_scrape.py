import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_dateutil


def search_wikipedia_for_page(title):
    """Use Wikipedia's API to search for a page and handle redirections and disambiguation."""
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": title,
        "utf8": 1,
        "srlimit": 1,
    }
    api_url = "https://en.wikipedia.org/w/api.php"
    response = requests.get(api_url, params=params).json()

    search_results = response.get("query", {}).get("search", [])
    if search_results:
        return "https://en.wikipedia.org/wiki/" + search_results[0]["title"].replace(
            " ", "_"
        )
    return None


def get_description(soup):
    """Extract the description from the soup object."""
    for p in soup.find_all("p"):
        if p.find("b"):
            return p.text
    return "Description not found."


def get_car_manufacturer_info(manufacturers):
    info = {}

    for manufacturer in manufacturers:
        page_url = search_wikipedia_for_page(manufacturer)
        if not page_url:
            info[manufacturer] = {
                "Description": "Page not found.",
                "Founding Year": None,
                "Country": None,
            }
            continue

        try:
            response = requests.get(page_url)
            soup = BeautifulSoup(response.text, "html.parser")

            description = get_description(soup)

            infobox = soup.find("table", {"class": "infobox"})
            year, country = None, None
            if infobox:
                for row in infobox.find_all("tr"):
                    header = row.find("th")
                    data = row.find("td")
                    if header and data:
                        header_text = header.text.strip().lower()
                        data_text = data.text.strip()
                        if "founded" in header_text:
                            year = data_text.split(";")[0].strip()
                        elif "headquarters" in header_text:
                            country = data_text.split(",")[-1].strip()

            info[manufacturer] = {
                "Description": description.strip(),
                "Founding Year": parse_dateutil(year),
                "Country": country,
            }
        except Exception as e:
            info[manufacturer] = {"Error": str(e)}

    return info


# Example usage
manufacturers = ["Lotus", "Ram", "Tesla"]
car_info = get_car_manufacturer_info(manufacturers)
for manufacturer, details in car_info.items():
    print(manufacturer, ":", details)

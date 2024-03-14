from concurrent.futures import ThreadPoolExecutor, as_completed
from ..base_scrape import BaseAPICommand
import requests
from carcomparer.cars.models import *
from bs4 import BeautifulSoup
from django.utils.dateparse import parse_date
from dateutil.parser import parse as parse_dateutil
import re


class ScrapeCarDataCommand(BaseAPICommand):  # Inherits from BaseAPICommand
    help = (
        "Scrapes Wikipedia to populate the database with up-to-date model information"
    )

    def scrape_manufacturers(self, year):
        manufacturers = Manufacturer.objects.all()

        # Use ThreadPoolExecutor to parallelize requests
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = [
                executor.submit(self.scrape_manufacturer_info, manufacturer.name)
                for manufacturer in manufacturers
            ]
            for future in futures:
                future.result()

    def scrape_manufacturer_info(self, manufacturer_name):
        page_url = self.search_wikipedia_for_page(manufacturer_name)
        if not page_url:
            self.stdout.write(
                self.style.ERROR(
                    f"Error Scraping {manufacturer_name}, Could not find Wikipedia Page"
                )
            )

        try:
            response = requests.get(page_url)
            soup = BeautifulSoup(response.text, "html.parser")
            description = self.get_description(soup)
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

                # Try to get the specific manufacturer by name
                manufacturer = Manufacturer.objects.get(name=manufacturer_name)
                year = self.extract_and_parse_date(year)

                # Update the fields
                manufacturer.country = (
                    self.clean_text(country)
                    if country is not None
                    else manufacturer.country
                )
                manufacturer.founded_date = year if year else manufacturer.founded_date
                manufacturer.description = (
                    description if description is not None else manufacturer.description
                )

                # Save the changes
                manufacturer.save()

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Updated {manufacturer_name} information successfully. {manufacturer.founded_date}"
                    )
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error Scraping {manufacturer_name}, {str(e)}")
            )

    def search_wikipedia_for_page(self, title):
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
            return "https://en.wikipedia.org/wiki/" + search_results[0][
                "title"
            ].replace(" ", "_")
        return None

    def clean_text(self, text):
        """
        Removes text within parentheses or brackets.
        """
        return re.sub(r"\[.*?\]|\(.*?\)", "", text).strip()

    def get_description(self, soup):
        """Extract and clean the description from the soup object."""
        for p in soup.find_all("p"):
            if p.find("b"):
                cleaned_text = self.clean_text(p.text)
                return cleaned_text
        return "Description not found."

    def extract_and_parse_date(self, date_string):
        # Try to find a date-like substring (e.g., "October 1946" or "1946-10")
        # This regex looks for patterns like "October 1946", "1946-10", or "24 September 1948"
        match = re.search(
            r"(\b\d{4}\b)|(\b\w+ \d{4}\b)|(\b\d{4}-\d{1,2}\b)|(\b\d{1,2} \w+ \d{4}\b)",
            date_string,
        )
        if match:
            try:
                # Parse the matched date-like substring
                parsed_date = parse_dateutil(match.group())
                return parsed_date
            except ValueError:
                # Return None or some indication that parsing failed
                return None
        else:
            # No date-like substring was found
            return "None"


Command = ScrapeCarDataCommand

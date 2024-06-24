from concurrent.futures import ThreadPoolExecutor, as_completed
from ..base_scrape import BaseAPICommand
import requests
from carcomparer.cars.models import *
from bs4 import BeautifulSoup
from django.utils.dateparse import parse_date
from dateutil.parser import parse as parse_dateutil
import re


class ScrapeCarDataCommand(BaseAPICommand):  # Inherits from BaseAPICommand
    help = "Scrapes Google to populate the database with up-to-date car information"

    def scrape_variations(self, year):
        cars = ModelYear.objects.all()

        # Use ThreadPoolExecutor to parallelize requests
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = [
                executor.submit(self.scrape_variation_google, car.full_name, car)
                for car in cars[100:150]
            ]
            for future in futures:
                future.result()

    def scrape_variation_google(self, car_name, car_model_year_obj):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36"
        }
        search_query = car_name.replace(" ", "+") + "+configurations"
        url = f"https://www.google.com/search?q={search_query}"
        try:
            response = requests.get(url, headers=headers)

            # print response status code and print that there was an error if the status code is not 200
            print(f"Response status code: {response.status_code}")

            if response.status_code == "429":
                self.style.ERROR("Too many requests")
                return

            soup = BeautifulSoup(response.text, "html.parser")

            # Find the link that contains the text 'Configurations', case-insensitive
            configurations_link = soup.find(
                "a", href=True, text=lambda t: t and "configurations" in t.lower()
            )
            configurations_url = configurations_link["href"]

            if configurations_url.startswith("/"):
                configurations_url = f"https://www.google.com{configurations_url}"

            # Fetch configurations page
            config_response = requests.get(configurations_url, headers=headers)
            config_response.raise_for_status()
            config_soup = BeautifulSoup(config_response.text, "html.parser")

            # first find the <g-scrolling-carousel> element that contains all the configurations
            scrolling_carousel = config_soup.find("g-scrolling-carousel")

            # save the scrolling carousel to a file for debugging
            with open(f"{car_name}.html", "w") as f:
                f.write(str(scrolling_carousel))

            # if the scrolling carousel is not found, throw an error
            if scrolling_carousel is None:
                raise Exception("No configurations found")

            # iterate through all child elements of the html and find all divs with classes that contain klitem-tr
            klitem_trs = config_soup.find_all("a", class_=re.compile("klitem-tr"))

            # iterate through all klitem_trs and get all text for each item in the tree
            for klitem_tr in klitem_trs:
                variation_text = klitem_tr.get_text()
                # Split the text, the string "From $" splits the text into variation and price
                variation, price = variation_text.split("From $")

                # turn the price into a number
                price = int(price.replace(",", ""))

                # Create a new CarVariation object for each variation found
                variation, created = Variation.objects.get_or_create(
                    model_year=car_model_year_obj, name=variation
                )

                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f"Added new car variation: {variation}")
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f"Existing variation: {variation}")
                    )

                # Add the price to the variation
                price = Price.objects.create(car=variation, price=price, currency="USD")

                self.stdout.write(
                    self.style.SUCCESS(f"Added price for variation: {price}")
                )

                print(f"Car Name: {car_name}, Variation: {variation}, Price: {price}")

            # else:
            #     print(f"No configurations link found for {url}")
        except Exception as e:
            print(f"Error scraping Google search results for {car_name}: {str(e)}")


Command = ScrapeCarDataCommand

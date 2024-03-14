from ..base_scrape import BaseAPICommand
import xml.etree.ElementTree as ET
from datetime import datetime
from carcomparer.cars.models import *
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.db.models import Q


class ScrapeCarDataCommand(BaseAPICommand):
    help = "Scrapes car data from FuelEconomy.gov"

    def scrape_manufacturers(self, year):
        url = f"https://www.fueleconomy.gov/ws/rest/vehicle/menu/make?year={year}"
        response = requests.get(url)
        if response.status_code != 200:
            self.stdout.write(
                self.style.ERROR("Error accessing the FuelEconomy.gov API")
            )
            return []

        root = ET.fromstring(response.content)
        for menuItem in root.findall("menuItem"):
            name = menuItem.find("value").text

            manufacturer, created = Manufacturer.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added new manufacturer: {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Existing manufacturer: {name}"))

    def scrape_variations(self, year):
        manufacturers = Manufacturer.objects.all()

        # Use ThreadPoolExecutor to parallelize requests
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = [
                executor.submit(
                    self.scrape_variations_manufacturer, year, manufacturer.name
                )
                for manufacturer in manufacturers
            ]
            for future in futures:
                future.result()  # Wait for all futures to complete

    def scrape_variations_manufacturer(self, year, manufacturer_name):
        url = f"https://www.fueleconomy.gov/ws/rest/vehicle/menu/model?year={year}&make={manufacturer_name}"
        response = requests.get(url)

        if response.status_code == 200:
            root = ET.fromstring(response.content)
            for menuItem in root.findall("menuItem"):
                full_model_name = menuItem.find("text").text
                # Split the full model name into all possible parts
                parts = full_model_name.split(" ")

                for i in range(len(parts), 0, -1):
                    # Attempt to match the model name starting from the longest possible match
                    potential_model_name = " ".join(parts[:i])
                    model_qs = Model.objects.filter(
                        Q(name__icontains=potential_model_name),
                        year=year,
                        manufacturer__name__icontains=manufacturer_name,
                    )

                    if model_qs.exists():
                        # If a matching model is found, determine the variation name
                        variation_name = (
                            " ".join(parts[i:]) if i < len(parts) else "Base"
                        )
                        model_instance = model_qs.first()
                        # Create a new variation for the model
                        Variation.objects.get_or_create(
                            model=model_instance, name=variation_name
                        )
                        self.stdout.write(
                            f"Added variation '{variation_name}' to model '{model_instance}'."
                        )
                        break  # Break the loop once the matching model is found and variation created
                    else:
                        # If no matching model is found after checking all combinations
                        self.stdout.write(
                            f"No matching model found for '{full_model_name}'."
                        )
        else:
            self.stdout.write(
                f"Failed to fetch variations for {year} {manufacturer_name}."
            )


Command = ScrapeCarDataCommand

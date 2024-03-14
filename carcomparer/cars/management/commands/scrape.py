from django.core.management.base import BaseCommand
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from carcomparer.cars.models import (
    CarManufacturer,
    CarModel,
    CarVariation,
)


class Command(BaseCommand):
    help = "Scrapes FuelEconomy.gov to populate the database with car manufacturers and models"

    def scrape_manufacturers(self, year):
        url = f"https://www.fueleconomy.gov/ws/rest/vehicle/menu/make?year={year}"
        response = requests.get(url)
        if response.status_code != 200:
            self.stdout.write(
                self.style.ERROR("Error accessing the FuelEconomy.gov API")
            )
            return []

        root = ET.fromstring(response.content)
        manufacturers = []
        for menuItem in root.findall("menuItem"):
            name = menuItem.find("value").text
            manufacturers.append(name)

            manufacturer, created = CarManufacturer.objects.get_or_create(name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Added new manufacturer: {name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Existing manufacturer: {name}"))
        return manufacturers

    def scrape_cars(self, year, manufacturer_name):
        known_exceptions = [
            "Model 3",
            "Model S",
            "Model X",
            "Model Y",
            # Add any other known exceptions here
        ]

        url = f"https://www.fueleconomy.gov/ws/rest/vehicle/menu/model?year={year}&make={manufacturer_name}"
        response = requests.get(url)
        if response.status_code != 200:
            self.stdout.write(
                self.style.ERROR("Error accessing the FuelEconomy.gov API")
            )
            return

        root = ET.fromstring(response.content)
        manufacturer = CarManufacturer.objects.get(name=manufacturer_name)
        for menuItem in root.findall("menuItem"):
            full_model_name = menuItem.find("value").text
            model_name, variation_name = self.parse_model_name(
                full_model_name, known_exceptions
            )
            car_model, created = CarModel.objects.get_or_create(
                manufacturer=manufacturer,
                name=model_name,
                year=year,
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Added model: {manufacturer_name} {model_name}")
                )

            # Assume default fuel type for simplicity, further refinement needed for accurate data
            CarVariation.objects.get_or_create(
                model=car_model,
                name=variation_name,
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f"Added/Updated variation: {model_name} {variation_name}"
                )
            )

    def parse_model_name(self, full_model_name, known_exceptions):
        for exception in known_exceptions:
            if full_model_name.startswith(exception):
                # If the full model name starts with a known exception, treat the rest as the variation
                variation_name = full_model_name[len(exception) :].strip()
                return exception, variation_name if variation_name else "Standard"

        # If no exception matches, split by the first space as a fallback
        parts = full_model_name.split(" ", 1)
        model_name = parts[0]
        variation_name = parts[1] if len(parts) > 1 else "Standard"
        return model_name, variation_name

    def handle(self, *args, **kwargs):
        current_year = datetime.now().year
        for year in range(2023, current_year + 1):  # Including the current year
            manufacturers = self.scrape_manufacturers(year)
            for manufacturer in manufacturers:
                self.scrape_cars(year, manufacturer)

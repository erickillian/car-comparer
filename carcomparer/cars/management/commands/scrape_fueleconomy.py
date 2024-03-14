from ..base_scrape import BaseAPICommand
import xml.etree.ElementTree as ET
from datetime import datetime
from carcomparer.cars.models import Manufacturer
import requests


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


Command = ScrapeCarDataCommand

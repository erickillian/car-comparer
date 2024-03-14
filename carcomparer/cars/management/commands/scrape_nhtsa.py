from concurrent.futures import ThreadPoolExecutor, as_completed
from ..base_scrape import BaseAPICommand
import requests
from carcomparer.cars.models import *


class ScrapeNHTSACommand(BaseAPICommand):  # Inherits from BaseAPICommand
    help = "Scrapes NHTSA to populate the database with up-to-date model information"

    def scrape_models(self, year):
        manufacturers = Manufacturer.objects.all()

        # Use ThreadPoolExecutor to parallelize requests
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = [
                executor.submit(
                    self.scrape_models_for_manufacturer, year, manufacturer.name
                )
                for manufacturer in manufacturers
            ]
            for future in futures:
                future.result()  # Wait for all futures to complete

    def scrape_models_for_manufacturer(self, year, manufacturer_name):
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/getmodelsformakeyear/make/{manufacturer_name}/modelyear/{year}?format=json"
        response = requests.get(url)
        if response.status_code != 200:
            self.stdout.write(
                self.style.ERROR(
                    f"Error accessing the NHTSA API for {manufacturer_name}"
                )
            )
            return

        data = response.json()
        if data["Count"] > 0:
            manufacturer, _ = Manufacturer.objects.get_or_create(name=manufacturer_name)
            for model in data["Results"]:
                model_name = model["Model_Name"]
                car_model, created = Model.objects.get_or_create(
                    manufacturer=manufacturer,
                    name=model_name,
                    year=year,
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Added model: {manufacturer_name} {model_name}"
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f"Existing model: {manufacturer_name} {model_name}"
                        )
                    )

    def scrape_vehicle_types(self, year):
        manufacturers = Manufacturer.objects.all()

        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            future_to_manufacturer = {
                executor.submit(
                    self.update_all_vehicle_types, manufacturer, year
                ): manufacturer
                for manufacturer in manufacturers
            }
            for future in as_completed(future_to_manufacturer):
                manufacturer = future_to_manufacturer[future]
                try:
                    future.result()
                except Exception as exc:
                    self.stdout.write(
                        self.style.ERROR(
                            f"{manufacturer.name} generated an exception: {exc}"
                        )
                    )

    def update_all_vehicle_types(self, manufacturer, year):
        vehicle_types = self.fetch_vehicle_types_for_manufacturer(manufacturer.name)
        for vehicle_type_name in vehicle_types:
            self.update_vehicle_types(manufacturer, year, vehicle_type_name)

    def fetch_vehicle_types_for_manufacturer(self, manufacturer_name):
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/GetVehicleTypesForMake/{manufacturer_name}?format=json"
        response = requests.get(url)
        vehicle_types = []
        if response.status_code == 200:
            data = response.json()
            for item in data.get("Results", []):
                vehicle_type_name = item["VehicleTypeName"]
                VehicleType.objects.get_or_create(name=vehicle_type_name)
                vehicle_types.append(vehicle_type_name)
        return vehicle_types

    def update_vehicle_types(self, manufacturer, year, vehicle_type_name):
        url = f"https://vpic.nhtsa.dot.gov/api/vehicles/getmodelsformakeyear/make/{manufacturer.name}/modelyear/{year}/vehicleType/{vehicle_type_name}?format=json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Get or create the VehicleType object outside the loop.
            vehicle_type, _ = VehicleType.objects.get_or_create(name=vehicle_type_name)
            updated_models_count = 0  # To keep track of how many models were updated.
            for item in data.get("Results", []):
                model_name = item["Model_Name"]
                # Try to update the vehicle_type for existing models.
                updated = Model.objects.filter(
                    manufacturer=manufacturer, name=model_name, year=year
                ).update(vehicle_type=vehicle_type)
                if updated:
                    updated_models_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Updated vehicle type for: {year} {manufacturer.name} {model_name} to {vehicle_type_name}"
                        )
                    )
                else:
                    # Optional: Log if a model was expected but not found.
                    self.stdout.write(
                        self.style.WARNING(
                            f"No existing model found to update: {year} {manufacturer.name} {model_name}"
                        )
                    )
            self.stdout.write(
                self.style.SUCCESS(f"Total models updated: {updated_models_count}")
            )


# This ensures Django finds this as the command to run
Command = ScrapeNHTSACommand

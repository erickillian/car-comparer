from django.core.management.base import BaseCommand
from datetime import datetime


class BaseAPICommand(BaseCommand):
    help = "Base command for scraping data from APIs"

    def add_arguments(self, parser):
        parser.add_argument(
            "--start-year",
            type=int,
            required=True,
            help="The start year for scraping data",
        )
        parser.add_argument(
            "--end-year",
            type=int,
            help="The optional end year for scraping data",
            default=datetime.now().year,
        )
        parser.add_argument(
            "--scrape-type",
            type=str,
            required=True,
            choices=["manufacturers", "models", "variations", "vehicle_types"],
            help="The type of data to scrape",
        )
        parser.add_argument(
            "--num-workers",
            type=int,
            required=False,
            default=10,
            help="Number of workers to use for parallel scraping",
        )

    def handle(self, *args, **kwargs):
        start_year = kwargs["start_year"]
        end_year = kwargs.get("end_year", start_year)
        scrape_type = kwargs["scrape_type"]
        self.num_workers = kwargs["num_workers"]

        # Dynamically call the appropriate scraping function based on scrape_type
        if hasattr(self, f"scrape_{scrape_type}"):
            scrape_function = getattr(self, f"scrape_{scrape_type}")
            for year in range(start_year, end_year + 1):
                self.stdout.write(f"Scraping {scrape_type} for year: {year}")
                scrape_function(year)
        else:
            self.stdout.write(
                self.style.ERROR(
                    f"No scraping function defined for type: {scrape_type}"
                )
            )

    def scrape_manufacturers(self, year):
        """Scrape manufacturers - to be overridden by subclass"""
        raise NotImplementedError("This method should be overridden in a subclass")

    def scrape_models(self, year):
        """Scrape models - to be overridden by subclass"""
        raise NotImplementedError("This method should be overridden in a subclass")

    def scrape_variations(self, year):
        """Scrape variations - to be overridden by subclass"""
        raise NotImplementedError("This method should be overridden in a subclass")

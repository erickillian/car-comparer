# this command removes duplicate models from the database

from django.core.management.base import BaseCommand
from carcomparer.cars.models import Manufacturer, Model
from django.db.models import Count


class Command(BaseCommand):
    help = "Removes duplicate models from the database"

    def handle(self, *args, **kwargs):
        # Annotate models with a count of duplicates based on 'manufacturer', 'name', and 'year'
        duplicates = (
            Model.objects.values("manufacturer", "name", "year")
            .annotate(model_count=Count("id"))
            .filter(model_count__gt=1)
        )

        for duplicate in duplicates:
            # Fetch the IDs of all models matching the duplicate criteria, except for the first one
            model_ids_to_delete = Model.objects.filter(
                manufacturer=duplicate["manufacturer"],
                name=duplicate["name"],
                year=duplicate["year"],
            ).values_list("id", flat=True)[
                1:
            ]  # Skip the first one to keep

            # Delete all models found in the previous step
            Model.objects.filter(id__in=model_ids_to_delete).delete()

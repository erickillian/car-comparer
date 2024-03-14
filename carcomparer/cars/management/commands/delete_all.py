from django.core.management.base import BaseCommand
import requests
import xml.etree.ElementTree as ET
from carcomparer.cars.models import *
from datetime import datetime


class Command(BaseCommand):
    help = "Deletes all cars in the database"

    def handle(self, *args, **kwargs):
        Manufacturer.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("All cars have been deleted"))

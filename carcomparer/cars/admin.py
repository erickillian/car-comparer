from django.contrib import admin
from django.apps import apps
from .models import *

# Replace 'car' with the name of your app
app_config = apps.get_app_config("cars")


@admin.register(Manufacturer)
class CarManufacturerAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Model)
class CarManufacturerAdmin(admin.ModelAdmin):
    search_fields = ["manufacturer__name", "name"]
    list_filter = ["manufacturer", "vehicle_type"]


@admin.register(Variation)
class CarManufacturerAdmin(admin.ModelAdmin):
    search_fields = [
        "model_year__model__manufacturer__name",
        "model_year__model__name",
        "name",
    ]
    list_filter = ["model_year__model__manufacturer", "model_year__model__vehicle_type"]


for model in app_config.get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        # This model is already registered
        pass

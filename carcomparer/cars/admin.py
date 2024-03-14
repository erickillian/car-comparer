from django.contrib import admin
from django.apps import apps

# Replace 'car' with the name of your app
app_config = apps.get_app_config("cars")

for model in app_config.get_models():
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        # This model is already registered
        pass

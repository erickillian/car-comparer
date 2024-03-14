from django.db import models


# Eg. Toyota, Ford, Honda, etc.
class Manufacturer(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=50, blank=True)
    founded_date = models.DateField(null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# Truck, Motorcycle, Passenger Car etc.
class VehicleType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# Eg. Camry, F-150, Civic, etc.
class Model(models.Model):
    manufacturer = models.ForeignKey(
        Manufacturer, related_name="models", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    vehicle_type = models.ForeignKey(
        VehicleType,
        related_name="models",
        on_delete=models.CASCADE,
        null=True,
    )

    @property
    def full_name(self):
        return f"{self.manufacturer.name} {self.name}"

    def __str__(self):
        return self.full_name

    class Meta:
        unique_together = ["manufacturer", "name"]


class ModelYear(models.Model):
    model = models.ForeignKey(
        Model, related_name="model_years", on_delete=models.CASCADE
    )
    year = models.PositiveSmallIntegerField()

    @property
    def full_name(self):
        return f"{self.year} {self.model.full_name}"

    def __str__(self):
        return self.full_name

    class Meta:
        unique_together = ["model", "year"]


# Eg. XLE, LX, EX, etc.
class Variation(models.Model):
    # FUEL_TYPE_CHOICES = [
    #     ("G", "Gasoline"),
    #     ("D", "Diesel"),
    #     ("E", "Electric"),
    #     ("H", "Hybrid"),
    # ]
    # fuel_type = models.CharField(max_length=1, choices=FUEL_TYPE_CHOICES, default="G")

    model_year = models.ForeignKey(
        ModelYear, related_name="variations", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)  # e.g., "Sport", "LX", "GT"

    @property
    def full_name(self):
        return f"{self.model_year.full_name} {self.name}"

    def __str__(self):
        return self.full_name


class Price(models.Model):
    car = models.OneToOneField(
        Variation, related_name="prices", on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.car.full_name} - {self.price} {self.currency}"

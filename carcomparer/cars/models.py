from django.db import models


# Eg. Toyota, Ford, Honda, etc.
class CarManufacturer(models.Model):
    name = models.CharField(max_length=100)
    country = models.CharField(max_length=50, blank=True)
    founded_date = models.DateField(null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# Eg. Camry, F-150, Civic, etc.
class CarModel(models.Model):
    manufacturer = models.ForeignKey(
        CarManufacturer, related_name="models", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)
    year = models.PositiveSmallIntegerField()
    description = models.TextField(blank=True, null=True)

    @property
    def full_name(self):
        return f"{self.year} {self.manufacturer.name} {self.name}"

    def __str__(self):
        return self.full_name


# Eg. XLE, LX, EX, etc.
class CarVariation(models.Model):
    FUEL_TYPE_CHOICES = [
        ("G", "Gasoline"),
        ("D", "Diesel"),
        ("E", "Electric"),
        ("H", "Hybrid"),
    ]
    model = models.ForeignKey(
        CarModel, related_name="variations", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=100)  # e.g., "Sport", "LX", "GT"
    fuel_type = models.CharField(max_length=1, choices=FUEL_TYPE_CHOICES, default="G")

    @property
    def full_name(self):
        return f"{self.model.full_name} {self.name}"

    def __str__(self):
        return self.full_name


class CarPrice(models.Model):
    car = models.OneToOneField(
        CarVariation, related_name="prices", on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default="USD")
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.car.full_name} - {self.price} {self.currency}"

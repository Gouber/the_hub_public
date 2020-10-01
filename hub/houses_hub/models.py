from django.db import models
from login_register_service_hub.models import CustomUser
from localflavor.gb.forms import GBCountySelect, GBPostcodeField


# Create your models here.
class Address(models.Model):
    street_address = models.CharField(max_length=200)
    city_or_town = models.CharField(max_length=40)
    county = GBCountySelect()
    post_code = GBPostcodeField()


class House(models.Model):
    number_of_rooms = models.IntegerField(default=0)
    number_of_bathrooms = models.IntegerField(default=0)
    address = models.CharField(max_length=200)
    agency = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="owning_agency")
    lat = models.DecimalField(max_digits=15, decimal_places=12, null=True)
    lgn = models.DecimalField(max_digits=15, decimal_places=12, null=True)
    price = models.IntegerField(default=0)


    def __str__(self):
        return self.address

    # Need to implement this after more parameters are added to the house model
    def equals(self, house):
        pass


class HousePicture(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    picture = models.ImageField()


class Lease(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    expiration_date = models.DateTimeField()


    def __str__(self):
        return self.house.address


class Application(models.Model):
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    students = models.ManyToManyField(CustomUser)
    submitted = models.BooleanField(default=False)

    def __str__(self):
        return self.house.address + "-" + self.applicationinfo_set.all().first().student.email


class ApplicationInfo(models.Model):
    personal_details = models.CharField(max_length=2000)
    money = models.CharField(max_length=200)
    letter_of_recommendation = models.CharField(max_length=2000)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    # Maybe change to non-nullable done to keep database
    application = models.ForeignKey(Application, on_delete=models.CASCADE, null=True, blank=True)

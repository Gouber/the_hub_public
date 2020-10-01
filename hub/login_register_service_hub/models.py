from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    USERTYPE_CHOICES = [(1, "STUDENT"), (2, "AGENCY"), (3, "SINGLE_AGENT"), (4, 'PRIVATE LANDLORD')]
    USERTYPE_DICT = {
        "STUDENT": 1,
        "AGENCY": 2,
        "SINGLE_AGENT": 3,
        "PRIVATE LANDLORD": 4
    }
    usertype = models.IntegerField(choices=USERTYPE_CHOICES, default=1)
    agency = models.CharField(max_length=200, null=True, blank=True)
    lease = models.ManyToManyField('houses_hub.Lease', blank=True,
                                   related_name='students')
    email = models.EmailField(unique=True, null=False, blank=False, )

    REQUIRED_FIELDS = ["email"]

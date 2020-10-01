import datetime
from django.db import models
from django.utils import timezone
from login_register_service_hub.models import CustomUser
from houses_hub.models import House
# Create your models here.


class Issue (models.Model):
    title = models.CharField(max_length = 200)
    pub_date = models.DateTimeField()
    house = models.ForeignKey(House, on_delete=models.CASCADE)
    closed = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)
    def __str__(self):
        return self.title

    def get_creator(self):
        return self.message_set.all().first().sender

class Message (models.Model):
    text = models.CharField(max_length = 20000)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    date_sent = models.DateTimeField()
    def __str__(self):
        return "Message "+str(self.id)+"-"+self.issue.title

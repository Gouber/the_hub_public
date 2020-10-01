from django.db import models
from django.utils import timezone, dateformat

from login_register_service_hub.models import CustomUser


class Conversation(models.Model):
    start_date = models.DateTimeField(default=timezone.now)
    students = models.ManyToManyField(CustomUser)

    def __str__(self):
        return ",".join(list(str(s) for s in self.students.all())) + " @ " + str(
            dateformat.format(self.start_date, 'Y-m-d H:i:s'))


class Chat(models.Model):
    date_sent = models.DateTimeField(default=timezone.now)
    message = models.CharField(max_length=500)
    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return str(self.student) + " @ " + str(dateformat.format(self.date_sent, 'Y-m-d H:i:s')) + ": " + self.message
# Create your models here.

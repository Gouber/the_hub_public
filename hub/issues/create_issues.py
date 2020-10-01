
from django.utils import timezone
from houses_hub.models import House, Lease
from .models import Issue, Message


def create_issue(title, message, user, house, hidden=False ):
    pub_date = timezone.now()
    issue = Issue.objects.create(title=title, pub_date=pub_date, closed=False, house=house, hidden=hidden)
    Message.objects.create(text=message, issue=issue, date_sent=pub_date, sender=user)
    return issue.id


from .models import House, Lease
from django.utils import timezone
from datetime import timedelta
from login_register_service_hub.create_users import create_student, create_agency


def create_house(address: str, agency):
    return House.objects.create(address=address, agency=agency)


def create_lease(house):
    return Lease.objects.create(house=house, expiration_date=timezone.now())

def create_student_with_lease(email,house):
    vlad_user = create_student(email)
    lease = Lease(house=house, expiration_date=timezone.now() + timedelta(days=30))
    #Note how you need to save the lease here otherwise django complains
    lease.save()
    vlad_user.lease.clear()
    vlad_user.lease.add(lease)
    #WE NEED TO SAVE BECAUSE WE ASSIGN A LEASE TO IT
    vlad_user.save()
    return vlad_user

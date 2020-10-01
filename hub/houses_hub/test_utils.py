from .models import House, Application, ApplicationInfo, Lease
from login_register_service_hub.models import CustomUser
from django import forms
# Dictionary used when an application with no extra students is created
no_extra_students_dict = {'none': [-1]}


def create_house(address: str, agency_name: str):
    agency = create_agency(agency_name)
    return House.objects.create(address=address, agency=agency)


def create_lease(house: House, expiration_date: forms.DateTimeField()) -> Lease:
    return Lease.objects.create(house=house, expiration_date=expiration_date)


def create_student(name):
    return CustomUser.objects.create(username=name, email='%s@gmail.com' % name)


def create_application(house, submitted, extra_students, creator, personal_details, money, letter_of_recommendation):
    application = Application.objects.create(house=house, submitted=submitted)
    if extra_students != no_extra_students_dict['none']:
        for identifier in extra_students:
            student = CustomUser.objects.get(pk=identifier)
            application.students.add(student)
        application.save()
    application_info = ApplicationInfo.objects.create(student=creator, application=application,
                                                      personal_details=personal_details, money=money,
                                                      letter_of_recommendation=letter_of_recommendation)
    return application, application_info


def create_application_simple(house, submitted):
    return Application.objects.create(house=house, submitted=submitted)


def create_agency(name):
    return CustomUser.objects.create(usertype=2, username=name, email='%s@gmail.com' % name)


def create_agent(name, agency):
    return CustomUser.objects.create(usertype=3, username=name, agency=agency, email='%s@gmail.com' % name)


def create_house_passing_agency(address, agency):
    return House.objects.create(address=address, agency=agency)

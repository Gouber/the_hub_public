from .forms import *


# CustomUser doesn't implement any methods no need for testing
def create_student(email):
    return CustomUser.objects.create_user(email=email, password="l4858uuu", username=email.split("@")[0], usertype=1)


def create_student_register_post_data(email):
    return {'email': email, 'password': "l4858uuu"}


def create_agency(email):
    return CustomUser.objects.create_user(email=email, password="l4858uuu", username=email.split("@")[0], usertype=2)


def create_agency_register_post_data(email):
    return {'email': email, 'password': "l4858uuu", 'username': email.split("@")[0]}


def create_agent_passing_agency(email, agency):
    return CustomUser.objects.create_user(email=email, password="l4858uuu", username=email.split("@")[0],
                                          agency=agency.username, usertype=3, first_name="Vlad",
                                          last_name="Nistor")


def create_agent_register_post_data(email, agency):
    return {'email': email, 'password': "l4858uuu", 'username': email.split("@")[0],
            'agency': agency, 'first_name': "Vlad", 'last_name': "Nistor"}



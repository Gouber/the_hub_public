from typing import Final, Union, List

from django.http import Http404, HttpResponse
from django.urls import Resolver404
from django.shortcuts import get_object_or_404


from houses_hub.models import Application, ApplicationInfo
from login_register_service_hub.models import CustomUser

APPLICATION_DELETED: Final[str] = "Application deleted after user rejection"
APPLICATION_SUBMITTED: Final[str] = 'The application has been submitted'
APPLICATION_INFO_SAVED: Final[str] = 'The application information has been saved'
ERROR_STUDENT_NOT_IN_APPLICATION: Final[str] = 'Student is not in application'
ERROR_NOT_APPLICATION_INFO_OWNER: Final[str] = 'The application info does not belong to this user'
ERROR_INVALID_INPUT: Final[str] = 'Invalid input given'
ERROR_STUDENT_DOES_NOT_EXIST: Final[str] = "One or more students in the application are not registered"
ERROR_REPEATED_STUDENT: Final[str] =\
    "Some of the students are repeated, if you are the sender do not include your email"
ERROR_HOUSE_DOES_NOT_EXIST: Final[str] = 'House does not exist'



def extract_agency(agency_or_agent: CustomUser) -> CustomUser:
    if CustomUser.USERTYPE_DICT["AGENCY"] == agency_or_agent.usertype:
        return agency_or_agent
    else:
        return CustomUser.objects.get(username=agency_or_agent.agency, usertype=CustomUser.USERTYPE_DICT['AGENCY'])


def agency_owns_application_or_404(agency_or_agent: CustomUser, application_pk: str) -> Union[None, Application]:
    application: Union[Http404, Application] = get_object_or_404(Application, pk=application_pk)
    agency: CustomUser = extract_agency(agency_or_agent)
    if agency == application.house.agency:
        return application
    else:
        raise Resolver404


def student_pending_in_application_or_404(student: CustomUser, application_pk: str) -> Union[None, Application]:
    application: Union[Http404, Application] = get_object_or_404(Application, pk=application_pk)
    if student in application.students.all():
        return application
    else:
        raise Resolver404


def api_is_student_pending_in_application(student: CustomUser, application_pk: str) -> bool:
    try:
        application = Application.objects.get(pk=application_pk)
    except Application.DoesNotExist:
        return False
    if student not in application.students.all():
        return False
    return True


def is_last_student_to_accept_application(application_info: ApplicationInfo) -> bool:
    return not application_info.application.students.exists()


def is_email_of_unique_student_in_application(sender: CustomUser, student: CustomUser,
                                              accumulated_students: List[CustomUser]) -> bool:
    return student.usertype == CustomUser.USERTYPE_DICT["STUDENT"] and \
                                student != sender and student not in accumulated_students


def is_student(user: CustomUser) -> bool:
    if user.is_authenticated:
        if user.usertype == CustomUser.USERTYPE_DICT["STUDENT"]:
            return True
    return False


def student_owns_application_info_or_404(student: CustomUser, application_info_id: str):
    application_info: Union[Http404, ApplicationInfo] = get_object_or_404(ApplicationInfo, pk=application_info_id)
    if application_info.student == student and not application_info.application.submitted:
        return application_info
    else:
        raise Resolver404


def student_owns_application_info(student: CustomUser, application_info_pk: str):
    try:
        application_info = ApplicationInfo.objects.get(pk=application_info_pk)
    except ApplicationInfo.DoesNotExist:
        return False
    if student != application_info.student or application_info.application.submitted:
        return False
    return True

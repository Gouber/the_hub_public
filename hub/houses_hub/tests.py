from datetime import timedelta

from django.test import TestCase
from rest_framework.test import APITestCase

from .gapi import *
from login_register_service_hub.create_users import *
from django.urls import reverse
from django.utils import timezone

from login_register_service_hub.create_users import *
from .forms import CreateApplicationForm, UserInfoForm
from .gapi import *
from rest_framework.test import APITestCase
from rest_framework.utils import json
from .test_utils import *
from .view_utils import *
from .views import ERROR_REPEATED_STUDENT, ERROR_STUDENT_DOES_NOT_EXIST


class DistanceCalculator(TestCase):

    def test_long_lat_distance(self):
        # random postcode a
        lat1 = 51.490928
        lon1 = -0.2078363
        # random postcode b
        lat2 = 52.7680739
        lon2 = -1.2066949
        distance = GAPI.distance_between(lat1, lon1, lat2, lon2)
        self.assert_(abs(distance - 157.5) < 1, "Distance between a and b should be ~157.5")


class FormTests(TestCase):

    def test_create_application_form_empty(self):
        form = CreateApplicationForm(data={'students': ""})
        self.assertFalse(form.is_valid())

    def test_create_application_form_no_extra_students(self):
        form = CreateApplicationForm(data={'students': "none"})
        self.assertTrue(form.is_valid())

    def test_create_application_form_single_extra_students(self):
        form = CreateApplicationForm(data={'students': "test@test.com"})
        self.assertTrue(form.is_valid())

    def test_create_application_form_multiple_extra_students(self):
        form = CreateApplicationForm(data={'students': "test1@test.com;test2@test.com;test3@test.com"})
        self.assertTrue(form.is_valid())

    def test_user_info_form_personal_details_empty(self):
        form = UserInfoForm(data={'personal_details': "", 'letter_of_recommendation': 'TLOR', 'money': 'TM'})
        self.assertFalse(form.is_valid())

    def test_user_info_form_letter_of_recommendation_empty(self):
        form = UserInfoForm(data={'personal_details': "TPD", 'letter_of_recommendation': '', 'money': 'TM'})
        self.assertFalse(form.is_valid())

    def test_user_info_form_money_empty(self):
        form = UserInfoForm(data={'personal_details': "TPD", 'letter_of_recommendation': 'TLOR', 'money': ''})
        self.assertFalse(form.is_valid())

    def test_user_info_all_fields_given(self):
        form = UserInfoForm(data={'personal_details': "TPD", 'letter_of_recommendation': 'TLOR', 'money': 'TM'})
        self.assertTrue(form.is_valid())


class AcceptApplicationViewTests(APITestCase):

    # Checks that a user that is not logged in gets a 404 when accessing accept application
    # in post and get and when post is called no changes occur in the DB.
    def test_not_logged_in_user(self):
        house = create_house("Test house", "Test agency")
        application, _ = create_application(house=house, submitted=False, extra_students=no_extra_students_dict['none'],
                                            creator=create_student('Helper student'), personal_details="TPD",
                                            money='Test money', letter_of_recommendation='TLOR')
        get_response = self.client.get(reverse('houses_hub:accept_application', args=(application.id,)))
        self.assertEqual(get_response.status_code, 401)
        post_response = self.client.post(reverse('houses_hub:accept_application', args=(application.id,)),
                                         {'choice': 'Accept'})
        self.assertEqual(post_response.status_code, 401)
        application_after_request = Application.objects.get(pk=application.id)
        self.assertEqual(application.students, application_after_request.students)

    # Checks that an agency gets a 404 when accessing accept application
    # in post and get and when post is called no changes occur in the DB.
    def test_agency(self):
        house = create_house("Test house", "Test agency")
        student = create_student('Test student')
        application, _ = create_application(house=house, submitted=False, extra_students=no_extra_students_dict['none'],
                                            creator=student, personal_details="TPD", money='Test money',
                                            letter_of_recommendation='TLOR')
        self.client.force_login(house.agency)
        response = self.client.get(reverse('houses_hub:accept_application', args=(application.id,)))
        self.assertEqual(response.status_code, 403)
        post_response = self.client.post(reverse('houses_hub:accept_application', args=(application.id,)),
                                         {'choice': 'Accept'})
        self.assertEqual(post_response.status_code, 403)
        application_after_request = Application.objects.get(pk=application.id)
        self.assertEqual(application.students, application_after_request.students)
        self.assertFalse(ApplicationInfo.objects.filter(student=house.agency).exists())

    # Checks that an agent gets a 404 when accessing accept application
    # in post and get and when post is called no changes occur in the DB.
    def test_agent(self):
        house = create_house("Test house", "Test agency")
        application, _ = create_application(house=house, submitted=False, extra_students=no_extra_students_dict['none'],
                                            creator=create_student('Helper student'), personal_details="TPD",
                                            money='Test money', letter_of_recommendation='TLOR')
        agent = create_agent("Test Agent", house.agency.username)
        self.client.force_login(agent)
        response = self.client.get(reverse('houses_hub:accept_application', args=(application.id,)))
        self.assertEqual(response.status_code, 403)
        post_response = self.client.post(reverse('houses_hub:accept_application', args=(application.id,)),
                                         {'choice': 'Accept'})
        self.assertEqual(post_response.status_code, 403)
        application_after_request = Application.objects.get(pk=application.id)
        self.assertEqual(application.students, application_after_request.students)
        self.assertFalse(ApplicationInfo.objects.filter(student=agent).exists())

    # Checks that a student with no pending applications
    # gets a 404 when accessing accept application in post and get and when post is called no changes occur in the DB.
    def test_student_no_pending_applications(self):
        house = create_house("Test house", "Test agency")
        application, _ = create_application(house=house, submitted=False, extra_students=no_extra_students_dict['none'],
                                            creator=create_student('Helper student'), personal_details="TPD",
                                            money='Test money', letter_of_recommendation='TLOR')
        student = create_student("Student")
        self.client.force_login(student)
        response = self.client.get(reverse('houses_hub:accept_application', args=(application.id,)))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {'response': ERROR_STUDENT_NOT_IN_APPLICATION})
        post_response = self.client.post(reverse('houses_hub:accept_application', args=(application.id,)),
                                         {'choice': 'Accept'})
        self.assertEqual(post_response.status_code, 404)
        self.assertEqual(response.data, {'response': ERROR_STUDENT_NOT_IN_APPLICATION})
        application_after_request = Application.objects.get(pk=application.id)
        self.assertEqual(application.students, application_after_request.students)
        self.assertFalse(ApplicationInfo.objects.filter(student=student).exists())

    # Checks that a student with a pending application which
    # isn't the one in the url gets 404 when accessing accept that application.
    def test_student_different_pending_application(self):
        house = create_house("Test house", "Test agency")
        student = create_student("Test student")
        application, _ = create_application(house=house, submitted=False, extra_students=[student.id],
                                            creator=create_student('Helper student'), personal_details="TPD",
                                            money='Test money', letter_of_recommendation='TLOR')
        second_house = create_house("Second test house", "Second test agency")
        second_application, _ = create_application(house=second_house, submitted=False,
                                                   extra_students=no_extra_students_dict['none'],
                                                   creator=create_student('Second helper student'),
                                                   personal_details="TPD", money='Test money',
                                                   letter_of_recommendation='TLOR')
        self.client.force_login(student)
        response = self.client.get(reverse('houses_hub:accept_application', args=(second_application.id,)))
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data, {'response': ERROR_STUDENT_NOT_IN_APPLICATION})
        post_response = self.client.post(reverse('houses_hub:accept_application', args=(second_application.id,)),
                                         {'choice': 'Accept'})
        self.assertEqual(post_response.status_code, 404)
        self.assertEqual(response.data, {'response': ERROR_STUDENT_NOT_IN_APPLICATION})
        application_after_request = Application.objects.get(pk=application.id)
        self.assertEqual(application.students, application_after_request.students)
        self.assertFalse(ApplicationInfo.objects.filter(student=student).exists())

    # Checks that a student with a pending application
    # which is the one in the url gets 200 when accessing accept that application.
    # Then if post with accept received 302 and student gets removed
    # from many to many field but application still exists.
    def test_student_correct_pending_application_accept(self):
        house = create_house("Test house", 'Test agency')
        student = create_student("Test Student")
        application, _ = create_application(house=house, submitted=False, extra_students=[student.id],
                                            creator=create_student('Helper student'), personal_details="TPD",
                                            money='Test money', letter_of_recommendation='TLOR')
        self.client.force_login(student)
        response_get = self.client.get(reverse('houses_hub:accept_application', args=(application.id,)))
        self.assertEqual(response_get.status_code, 200)
        response_post = self.client.post(reverse('houses_hub:accept_application', args=(application.id,)),
                                         {'choice': 'Accept'})
        application = Application.objects.get(pk=application.id)
        self.assertEqual(response_post.status_code, 302)
        self.assertTrue(Application.objects.filter(pk=application.id).exists())
        self.assertFalse(application.students.exists())

    # Checks that a student with a pending application
    # which is the one in the url gets 200 when accessing accept that application.
    # Then if post with reject received 302 and application gets deleted
    def test_student_correct_pending_application_reject(self):
        house = create_house("Test house", 'Test agency')
        student = create_student("Test Student")
        application, _ = create_application(house=house, submitted=False, extra_students=[student.id],
                                            creator=create_student('Helper student'), personal_details="TPD",
                                            money='Test money', letter_of_recommendation='TLOR')
        self.client.force_login(student)
        response_get = self.client.get(reverse('houses_hub:accept_application', args=(application.id,)))
        self.assertEqual(response_get.status_code, 200)
        response_post = self.client.post(reverse('houses_hub:accept_application', args=(application.id,)),
                                         {'choice': 'Reject'})
        self.assertEqual(response_post.status_code, 302)
        self.assertFalse(Application.objects.filter(pk=application.id).exists())

    # Checks that a student that has already accepted an
    # application and tries to accept the same application again gets a 404 and can't create any changes in the DB
    # Such as duplicate ApplicationInfo 
    def test_student_correct_pending_application_accepted_try_to_accept_again(self):
        house = create_house("Test house", 'Test agency')
        student = create_student("Test Student")
        application, _ = create_application(house=house, submitted=False, extra_students=[student.id],
                                            creator=create_student('Helper student'), personal_details="TPD",
                                            money='Test money', letter_of_recommendation='TLOR')
        self.client.force_login(student)
        self.client.post(reverse('houses_hub:accept_application', args=(application.id,)),
                         {'choice': 'Accept'})
        application = Application.objects.get(pk=application.id)
        response_get = self.client.get(reverse('houses_hub:accept_application', args=(application.id,)))
        self.assertEqual(response_get.status_code, 404)
        post_response = self.client.post(reverse('houses_hub:accept_application', args=(application.id,)),
                                         {'choice': 'Accept'})
        self.assertEqual(post_response.status_code, 404)
        application_after_request = Application.objects.get(pk=application.id)
        self.assertEqual(application.students, application_after_request.students)
        self.assertEqual(len(ApplicationInfo.objects.filter(student=student)), 1)


class FillUserApplicationInfoViewTests(TestCase):

    # Test that an anonymous user gets a 404 when trying to edit the information of an application
    def test_not_logged_in_user(self):
        house = create_house("Test house", 'Test agency')
        application, info = create_application(house=house, submitted=False,
                                               extra_students=no_extra_students_dict['none'],
                                               creator=create_student("Creator"), personal_details="TPD",
                                               money='Test money', letter_of_recommendation='TLOR')
        response = self.client.get(reverse('houses_hub:fill_application_info', args=(info.id,)))
        self.assertEqual(response.status_code, 401)
        post_response = self.client.post(reverse('houses_hub:fill_application_info', args=(info.id,)),
                                         {'money': 'New money',
                                          'letter_of_recommendation': 'New letter of recommendation',
                                          'personal_details': 'New personal details', 'submit_application': 'yes'})
        self.assertEqual(post_response.status_code, 401)
        info_after_request = ApplicationInfo.objects.get(pk=info.id)
        application_after_request = Application.objects.get(pk=application.id)
        self.assertEqual(info.money, info_after_request.money)
        self.assertEqual(info.personal_details, info_after_request.personal_details)
        self.assertEqual(info.letter_of_recommendation, info_after_request.letter_of_recommendation)
        self.assertFalse(application_after_request.submitted)

    # Test that an agency gets a 404 when trying to edit the information of an application
    def test_agency(self):
        house = create_house("Test house", 'Test agency')
        application, info = create_application(house=house, submitted=False,
                                               extra_students=no_extra_students_dict['none'],
                                               creator=create_student("Creator"), personal_details="TPD",
                                               money='Test money', letter_of_recommendation='TLOR')
        self.client.force_login(house.agency)
        response = self.client.get(reverse('houses_hub:fill_application_info', args=(info.id,)))
        self.assertEqual(response.status_code, 403)
        post_response = self.client.post(reverse('houses_hub:fill_application_info', args=(info.id,)),
                                         {'money': 'New money',
                                          'letter_of_recommendation': 'New letter of recommendation',
                                          'personal_details': 'New personal details', 'submit_application': 'yes'})
        self.assertEqual(post_response.status_code, 403)
        info_after_request = ApplicationInfo.objects.get(pk=info.id)
        application_after_request = Application.objects.get(pk=application.id)
        self.assertEqual(info.money, info_after_request.money)
        self.assertEqual(info.personal_details, info_after_request.personal_details)
        self.assertEqual(info.letter_of_recommendation, info_after_request.letter_of_recommendation)
        self.assertFalse(application_after_request.submitted)

    # Test that an agent gets a 404 when trying to edit the information of an application
    def test_agent(self):
        house = create_house("Test house", 'Test agency')
        application, info = create_application(house=house, submitted=False,
                                               extra_students=no_extra_students_dict['none'],
                                               creator=create_student("Creator"), personal_details="TPD",
                                               money='Test money', letter_of_recommendation='TLOR')
        agent = create_agent("Test Agent", house.agency.username)
        self.client.force_login(agent)
        response = self.client.get(reverse('houses_hub:fill_application_info', args=(info.id,)))
        self.assertEqual(response.status_code, 403)
        post_response = self.client.post(reverse('houses_hub:fill_application_info', args=(info.id,)),
                                         {'money': 'New money',
                                          'letter_of_recommendation': 'New letter of recommendation',
                                          'personal_details': 'New personal details', 'submit_application': 'yes'})
        self.assertEqual(post_response.status_code, 403)
        info_after_request = ApplicationInfo.objects.get(pk=info.id)
        application_after_request = Application.objects.get(pk=application.id)
        self.assertEqual(info.money, info_after_request.money)
        self.assertEqual(info.personal_details, info_after_request.personal_details)
        self.assertEqual(info.letter_of_recommendation, info_after_request.letter_of_recommendation)
        self.assertFalse(application_after_request.submitted)

    # Test that a student who hasn't got an application gets 404
    def test_student_no_application(self):
        house = create_house("Test house", 'Test agency')
        application, info = create_application(house=house, submitted=False,
                                               extra_students=no_extra_students_dict['none'],
                                               creator=create_student('Creator'), personal_details="TPD",
                                               money='Test money', letter_of_recommendation='TLOR')
        client_student = create_student("Client student")
        self.client.force_login(client_student)
        response = self.client.get(reverse('houses_hub:fill_application_info', args=(info.id,)))
        self.assertEqual(response.status_code, 401)
        post_response = self.client.post(reverse('houses_hub:fill_application_info', args=(info.id,)),
                                         {'money': 'New money',
                                          'letter_of_recommendation': 'New letter of recommendation',
                                          'personal_details': 'New personal details', 'submit_application': 'yes'})
        self.assertEqual(post_response.status_code, 401)
        info_after_request = ApplicationInfo.objects.get(pk=info.id)
        application_after_request = Application.objects.get(pk=application.id)
        self.assertEqual(info.money, info_after_request.money)
        self.assertEqual(info.personal_details, info_after_request.personal_details)
        self.assertEqual(info.letter_of_recommendation, info_after_request.letter_of_recommendation)
        self.assertFalse(application_after_request.submitted)

    # Test that a student who is in a different application gets 404
    def test_student_different_application(self):
        first_house = create_house("First test house", 'First test agency')
        first_application, first_info = create_application(house=first_house, submitted=False,
                                                           extra_students=no_extra_students_dict['none'],
                                                           creator=create_student('First creator'),
                                                           personal_details="TPD", money='Test money',
                                                           letter_of_recommendation='TLOR')
        second_house = create_house("Second test house", 'Second test agency')
        client_student = create_student("Client student")
        create_application(house=second_house, submitted=False,
                           extra_students=no_extra_students_dict['none'],
                           creator=client_student, personal_details="TPD",
                           money='Test money', letter_of_recommendation='TLOR')
        self.client.force_login(client_student)
        response = self.client.get(reverse('houses_hub:fill_application_info', args=(first_info.id,)))
        self.assertEqual(response.status_code, 401)
        post_response = self.client.post(reverse('houses_hub:fill_application_info', args=(first_info.id,)),
                                         {'money': 'New money',
                                          'letter_of_recommendation': 'New letter of recommendation',
                                          'personal_details': 'New personal details', 'submit_application': 'yes'})
        self.assertEqual(post_response.status_code, 401)
        info_after_request = ApplicationInfo.objects.get(pk=first_info.id)
        application_after_request = Application.objects.get(pk=first_application.id)
        self.assertEqual(first_info.money, info_after_request.money)
        self.assertEqual(first_info.personal_details, info_after_request.personal_details)
        self.assertEqual(first_info.letter_of_recommendation, info_after_request.letter_of_recommendation)
        self.assertFalse(application_after_request.submitted)

    # Test that a student who hasn't accepted the application yet can't edit its information 
    def test_student_pending_application(self):
        house = create_house("Test house", 'Test agency')
        client_student = create_student('Client student')
        application, info = create_application(house=house, submitted=False, extra_students=[client_student.id],
                                               creator=create_student('Creator'), personal_details="TPD",
                                               money='Test money', letter_of_recommendation='TLOR')
        self.client.force_login(client_student)
        response = self.client.get(reverse('houses_hub:fill_application_info', args=(info.id,)))
        self.assertEqual(response.status_code, 401)
        post_response = self.client.post(reverse('houses_hub:fill_application_info', args=(info.id,)),
                                         {'money': 'New money',
                                          'letter_of_recommendation': 'New letter of recommendation',
                                          'personal_details': 'New personal details', 'submit_application': 'yes'})
        self.assertEqual(post_response.status_code, 401)
        info_after_request = ApplicationInfo.objects.get(pk=info.id)
        application_after_request = Application.objects.get(pk=application.id)
        self.assertEqual(info.money, info_after_request.money)
        self.assertEqual(info.personal_details, info_after_request.personal_details)
        self.assertEqual(info.letter_of_recommendation, info_after_request.letter_of_recommendation)
        self.assertFalse(application_after_request.submitted)

    # Test that a student in the application gets a 200 and can edit and save application information 
    def test_student_in_application_not_submit(self):
        house = create_house("Test house", 'Test agency')
        client_student = create_student('Client student')
        application, info = create_application(house=house, submitted=False,
                                               extra_students=[create_student("Test extra student").id],
                                               creator=client_student, personal_details="TPD", money='Test money',
                                               letter_of_recommendation='TLOR')
        self.client.force_login(client_student)
        response_get = self.client.get(reverse('houses_hub:fill_application_info', args=(info.id,)))
        self.assertEqual(response_get.status_code, 200)
        response_post = self.client.post(reverse('houses_hub:fill_application_info', args=(info.id,)),
                                         {'money': 'New money',
                                          'letter_of_recommendation': 'New letter of recommendation',
                                          'personal_details': 'New personal details'})
        self.assertEqual(response_post.status_code, 302)
        self.assertTrue(ApplicationInfo.objects.filter(pk=info.id).exists())
        info = ApplicationInfo.objects.get(pk=info.id)
        self.assertEqual(info.money, "New money")
        self.assertEqual(info.letter_of_recommendation, "New letter of recommendation")
        self.assertEqual(info.personal_details, "New personal details")

    # Test that a student in the application who is not last can't submit the application
    def test_student_in_application_not_last_cannot_submit(self):
        house = create_house("Test house", 'Test agency')
        client_student = create_student('Client student')
        application, info = create_application(house=house, submitted=False,
                                               extra_students=[create_student("Test extra student").id],
                                               creator=client_student, personal_details="TPD", money='Test money',
                                               letter_of_recommendation='TLOR')
        self.client.force_login(client_student)
        response_post = self.client.post(reverse('houses_hub:fill_application_info', args=(info.id,)),
                                         {'money': 'New money',
                                          'letter_of_recommendation': 'New letter of recommendation',
                                          'personal_details': 'New personal details', 'submit_application': 'yes'})
        self.assertEqual(response_post.status_code, 302)
        self.assertTrue(ApplicationInfo.objects.filter(pk=info.id).exists())
        info = ApplicationInfo.objects.get(pk=info.id)
        self.assertFalse(info.application.submitted)

    # Test that a student who is last and submits application gets submitted 
    def test_student_in_application_last_submits(self):
        house = create_house("Test house", 'Test agency')
        client_student = create_student('Client student')
        application, info = create_application(house=house, submitted=False,
                                               extra_students=no_extra_students_dict['none'],
                                               creator=client_student, personal_details="TPD", money='Test money',
                                               letter_of_recommendation='TLOR')
        self.client.force_login(client_student)
        response_post = self.client.post(reverse('houses_hub:fill_application_info', args=(info.id,)),
                                         {'money': 'New money',
                                          'letter_of_recommendation': 'New letter of recommendation',
                                          'personal_details': 'New personal details', 'submit_application': 'yes'})
        self.assertEqual(response_post.status_code, 302)
        self.assertTrue(ApplicationInfo.objects.filter(pk=info.id).exists())
        info = ApplicationInfo.objects.get(pk=info.id)
        self.assertEqual(info.money, "New money")
        self.assertEqual(info.letter_of_recommendation, "New letter of recommendation")
        self.assertEqual(info.personal_details, "New personal details")
        self.assertTrue(info.application.submitted)

    # Test that a student who is last and doesn't submit then application doesn't get submitted but information is saved 
    def test_student_in_application_last_does_not_submit(self):
        house = create_house("Test house", 'Test agency')
        client_student = create_student('Client student')
        application, info = create_application(house=house, submitted=False,
                                               extra_students=no_extra_students_dict['none'],
                                               creator=client_student, personal_details="TPD", money='Test money',
                                               letter_of_recommendation='TLOR')
        self.client.force_login(client_student)
        response_post = self.client.post(reverse('houses_hub:fill_application_info', args=(info.id,)),
                                         {'money': 'New money',
                                          'letter_of_recommendation': 'New letter of recommendation',
                                          'personal_details': 'New personal details', 'submit_application': 'no'})
        self.assertEqual(response_post.status_code, 302)
        self.assertTrue(ApplicationInfo.objects.filter(pk=info.id).exists())
        info = ApplicationInfo.objects.get(pk=info.id)
        self.assertEqual(info.money, "New money")
        self.assertEqual(info.letter_of_recommendation, "New letter of recommendation")
        self.assertEqual(info.personal_details, "New personal details")
        self.assertFalse(info.application.submitted)

    def test_student_in_submitted_application(self):
        house = create_house("Test house", 'Test agency')
        client_student = create_student('Client student')
        application, info = create_application(house=house, submitted=False,
                                               extra_students=no_extra_students_dict['none'],
                                               creator=client_student, personal_details="TPD", money='Test money',
                                               letter_of_recommendation='TLOR')
        self.client.force_login(client_student)
        self.client.post(reverse('houses_hub:fill_application_info', args=(info.id,)),
                         {'money': 'New money',
                          'letter_of_recommendation': 'New letter of recommendation',
                          'personal_details': 'New personal details', 'submit_application': 'yes'})
        response = self.client.get(reverse('houses_hub:fill_application_info', args=(info.id,)))
        self.assertEqual(response.status_code, 401)


class PendingApplicationIndexTests(APITestCase):
    # check content of JSONs when what's implemented
    def test_anonymous_user_can_access(self):
        response = self.client.get(reverse('houses_hub:pending_application_index'))
        self.assertEqual(response.status_code, 404)

    def test_agency_can_access(self):
        agency = create_agency("a@a.com")
        self.client.force_login(agency)
        response = self.client.get(reverse('houses_hub:pending_application_index'))
        self.assertEqual(response.status_code, 404)

    def test_student_can_access(self):
        student = create_student("b@b.com")
        self.client.force_login(student)
        response = self.client.get(reverse('houses_hub:pending_application_index'))
        self.assertEqual(response.status_code, 200)

    def test_agent_can_access(self):
        agent = create_agent_passing_agency("c@c.com", create_agency("b@g.com"))
        self.client.force_login(agent)
        response = self.client.get(reverse('houses_hub:pending_application_index'))
        self.assertEqual(response.status_code, 404)
    # check a created appliction appears in the index with .contains


class AcceptReceivedApplicationTests(APITestCase):
    def test_anonymous_user_cannot_access(self):
        house = create_house_passing_agency("Woodward Buildings", create_agency("a@a.com"))
        application = create_application_simple(house, True)
        post = json.dumps({"choice": "Accept"}, indent=4, default=str)
        post_response = self.client.post(
            reverse('houses_hub:accept_received_application', kwargs={'pk': application.pk}), data=post,
            content_type="application/json")
        self.assertEqual(post_response.status_code, 404)
        self.assertTrue(Application.objects.filter(pk=application.id).exists())
        self.assertFalse(Lease.objects.filter(house=house).exists())

    def test_student_cannot_access(self):
        student = create_student("b@b.com")
        self.client.force_login(student)
        house = create_house_passing_agency("Woodward Buildings", create_agency("a@a.com"))
        application = create_application_simple(house, True)
        post = json.dumps({"choice": "Accept"}, indent=4, default=str)
        post_response = self.client.post(
            reverse('houses_hub:accept_received_application', kwargs={'pk': application.pk}), data=post,
            content_type="application/json")
        self.assertEqual(post_response.status_code, 404)
        self.assertTrue(Application.objects.filter(pk=application.id).exists())
        self.assertFalse(Lease.objects.filter(house=house).exists())

    # agency accepts application
    def test_agency_accepts_application(self):
        agency = create_agency("a@a.com")
        self.client.force_login(agency)
        house = create_house_passing_agency("Woodward Buildings", agency)
        application = create_application_simple(house, True)
        post = json.dumps({"choice": "Accept"}, indent=4, default=str)
        post_response = self.client.post(
            reverse('houses_hub:accept_received_application', kwargs={'pk': application.pk}), data=post,
            content_type="application/json")
        self.assertEqual(post_response.status_code, 200)
        self.assertFalse(Application.objects.filter(pk=application.id).exists())
        self.assertTrue(Lease.objects.filter(house=house).exists())

    # agent accepts application
    def test_agent_accepts_application(self):
        agency = create_agency("a@a.com")
        agent = create_agent_passing_agency("c@c.com", agency)
        self.client.force_login(agent)
        house = create_house_passing_agency("Woodward Buildings", agency)
        application = create_application_simple(house, True)
        post = json.dumps({"choice": "Accept"}, indent=4, default=str)
        post_response = self.client.post(
            reverse('houses_hub:accept_received_application', kwargs={'pk': application.pk}), data=post,
            content_type="application/json")
        self.assertEqual(post_response.status_code, 200)
        self.assertFalse(Application.objects.filter(pk=application.id).exists())
        self.assertTrue(Lease.objects.filter(house=house).exists())

    # agency rejects application
    def test_agency_rejects_application(self):
        agency = create_agency("a@a.com")
        self.client.force_login(agency)
        house = create_house_passing_agency("Woodward Buildings", agency)
        application = create_application_simple(house, True)
        post = json.dumps({"choice": "Reject"}, indent=4, default=str)
        post_response = self.client.post(
            reverse('houses_hub:accept_received_application', kwargs={'pk': application.pk}), data=post,
            content_type="application/json")
        self.assertEqual(post_response.status_code, 200)
        self.assertFalse(Application.objects.filter(pk=application.id).exists())
        self.assertFalse(Lease.objects.filter(house=house).exists())

    # agency makes choice other than "Accept" or "Reject"
    def test_agency_makes_bad_choice(self):
        agency = create_agency("a@a.com")
        self.client.force_login(agency)
        house = create_house_passing_agency("Woodward Buildings", agency)
        application = create_application_simple(house, True)
        post = json.dumps({"choice": "badchoice"}, indent=4, default=str)
        post_response = self.client.post(
            reverse('houses_hub:accept_received_application', kwargs={'pk': application.pk}), data=post,
            content_type="application/json")
        # check no changes in db
        self.assertEqual(post_response.status_code, 404)
        self.assertTrue(Application.objects.filter(pk=application.id).exists())
        self.assertFalse(Lease.objects.filter(house=house).exists())

    # agencies cannot manage other agencies' applications
    def test_agency_accesses_not_owned_application(self):
        agency1 = create_agency("a@a.com")
        self.client.force_login(agency1)
        agency2 = create_agency("a2@a2.com")
        house = create_house_passing_agency("Woodward Buildings", agency2)
        application = create_application_simple(house, True)
        post = json.dumps({"choice": "Accept"}, indent=4, default=str)
        post_response = self.client.post(
            reverse('houses_hub:accept_received_application', kwargs={'pk': application.pk}), data=post,
            content_type="application/json")
        self.assertEqual(post_response.status_code, 404)
        self.assertTrue(Application.objects.filter(pk=application.id).exists())
        self.assertFalse(Lease.objects.filter(house=house).exists())

    # agents cannot manage other agencies' applications
    def test_agent_accesses_not_owned_application(self):
        agency1 = create_agency("a@a.com")
        agent = create_agent_passing_agency("c@c.com", agency1)
        self.client.force_login(agent)
        agency2 = create_agency("a2@a2.com")
        house = create_house_passing_agency("Woodward Buildings", agency2)
        application = create_application_simple(house, True)
        post = json.dumps({"choice": "Accept"}, indent=4, default=str)
        post_response = self.client.post(
            reverse('houses_hub:accept_received_application', kwargs={'pk': application.pk}), data=post,
            content_type="application/json")
        self.assertEqual(post_response.status_code, 404)
        self.assertTrue(Application.objects.filter(pk=application.id).exists())
        self.assertFalse(Lease.objects.filter(house=house).exists())


class ManagedHousesIndexTests(APITestCase):
    def test_anonymous_user_cannot_access(self):
        response = self.client.get(reverse('houses_hub:managed_houses'))
        self.assertEqual(response.status_code, 404)

    def test_agency_can_access(self):
        agency = create_agency("a@a.com")
        self.client.force_login(agency)
        response = self.client.get(reverse('houses_hub:managed_houses'))
        self.assertEqual(response.status_code, 200)

    def test_student_cannot_access(self):
        student = create_student("b@b.com")
        self.client.force_login(student)
        response = self.client.get(reverse('houses_hub:managed_houses'))
        self.assertEqual(response.status_code, 404)

    def test_agent_can_access(self):
        agent = create_agent_passing_agency("c@c.com", create_agency("b@g.com"))
        self.client.force_login(agent)
        response = self.client.get(reverse('houses_hub:managed_houses'))
        self.assertEqual(response.status_code, 200)


class EditApplicationIndexTests(APITestCase):
    def test_anonymous_user_cannot_access(self):
        response = self.client.get(reverse('houses_hub:edit_application_index'))
        self.assertEqual(response.status_code, 404)

    def test_agency_cannot_access(self):
        agency = create_agency("a@a.com")
        self.client.force_login(agency)
        response = self.client.get(reverse('houses_hub:edit_application_index'))
        self.assertEqual(response.status_code, 404)

    def test_student_cannot_access(self):
        student = create_student("b@b.com")
        self.client.force_login(student)
        response = self.client.get(reverse('houses_hub:edit_application_index'))
        self.assertEqual(response.status_code, 200)

    def test_agent_cannot_access(self):
        agent = create_agent_passing_agency("c@c.com", create_agency("b@g.com"))
        self.client.force_login(agent)
        response = self.client.get(reverse('houses_hub:edit_application_index'))
        self.assertEqual(response.status_code, 404)


class ReceivedApplicationsIndexTests(APITestCase):
    def test_anonymous_user_cannot_access(self):
        owning_agency = create_agency("owning@owning.com")
        house = create_house_passing_agency("Woodward Buildings", owning_agency)
        response = self.client.get(reverse('houses_hub:received_applications', kwargs={'pk': house.pk}))
        self.assertEqual(response.status_code, 404)

    def test_agency_can_access(self):
        agency = create_agency("a@a.com")
        self.client.force_login(agency)
        house = create_house_passing_agency("Woodward Buildings", agency)
        response = self.client.get(reverse('houses_hub:received_applications', kwargs={'pk': house.pk}))
        self.assertEqual(response.status_code, 200)

    def test_agency_doesnt_own_cannot_access(self):
        owning_agency = create_agency("owning@owning.com")
        agency = create_agency("a@a.com")
        self.client.force_login(agency)
        house = create_house_passing_agency("Woodward Buildings", owning_agency)
        response = self.client.get(reverse('houses_hub:received_applications', kwargs={'pk': house.pk}))
        self.assertEqual(response.status_code, 404)

    def test_student_cannot_access(self):
        student = create_student("b@b.com")
        self.client.force_login(student)
        owning_agency = create_agency("owning@owning.com")
        house = create_house_passing_agency("Woodward Buildings", owning_agency)
        response = self.client.get(reverse('houses_hub:received_applications', kwargs={'pk': house.pk}))
        self.assertEqual(response.status_code, 404)

    def test_agent_can_access(self):
        owning_agency = create_agency("owning@owning.com")
        agent = create_agent_passing_agency("c@c.com", owning_agency)
        self.client.force_login(agent)
        house = create_house_passing_agency("Woodward Buildings", owning_agency)
        response = self.client.get(reverse('houses_hub:received_applications', kwargs={'pk': house.pk}))
        self.assertEqual(response.status_code, 200)

    def test_agent_doesnt_own_cannot_access(self):
        owning_agency = create_agency("owning@owning.com")
        agent = create_agent_passing_agency("c@c.com", create_agency("another@another.com"))
        self.client.force_login(agent)
        house = create_house_passing_agency("Woodward Buildings", owning_agency)
        response = self.client.get(reverse('houses_hub:received_applications', kwargs={'pk': house.pk}))
        self.assertEqual(response.status_code, 404)


class CreateHouseTests(APITestCase):
    # Helper Function
    def create_house_using_post(self, address: str):
        post_data = json.dumps({"address": address}, indent=4, sort_keys=True, default=str)
        return self.client.post(reverse('houses_hub:create'), data=post_data, content_type="application/json")

    def test_anonymous_user_cannot_create(self):
        address = "woodward buildings"
        post_response = self.create_house_using_post(address)
        self.assertEqual(post_response.status_code, 404)
        self.assertFalse(House.objects.filter(address=address).exists())

    def test_agency_can_create(self):
        agency = create_agency("a@a.com")
        self.client.force_login(agency)
        address = "woodward buildings"
        post_response = self.create_house_using_post(address)
        self.assertEqual(post_response.status_code, 201)
        self.assertTrue(House.objects.filter(address=address).exists())

    def test_student_cannot_create(self):
        student = create_student("b@b.com")
        self.client.force_login(student)
        address = "woodward buildings"
        post_response = self.create_house_using_post(address)
        self.assertEqual(post_response.status_code, 404)
        self.assertFalse(House.objects.filter(address=address).exists())

    def test_agent_can_create(self):
        agency = create_agency("a@a.com")
        agent = create_agent_passing_agency("c@c.com", agency)
        self.client.force_login(agent)
        address = "woodward buildings"
        post_response = self.create_house_using_post(address)
        self.assertEqual(post_response.status_code, 201)
        self.assertTrue(House.objects.filter(address=address).exists())

    # Agency shouldn't be allowed to create a house that is already in the db.
    def test_create_house_twice(self):
        address = "Woodward Buildings"
        agency = create_agency("a@a.com")
        self.client.force_login(agency)
        response1 = self.create_house_using_post(address)
        response2 = self.create_house_using_post(address)
        self.assertEqual(response1.status_code, 201)
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(House.objects.filter(address=address).count(), 1)

    # Agency cannot be allowed to create house that cannot be found by the maps API
    def test_create_house_wrong_address(self):
        agency = create_agency("a@a")
        address = "idontexist"
        self.client.force_login(agency)
        response = self.create_house_using_post(address)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(House.objects.filter(address=address).exists())


class CreateApplicationViewTests(TestCase):

    # Test that a user that is not logged in gets 404 when trying to apply for a house
    def test_not_logged_in_user(self):
        house = create_house("Test house", 'Test agency')
        response = self.client.get(reverse('houses_hub:create_application', args=(house.id,)))
        self.assertEquals(response.status_code, 401)
        post_response = self.client.post(reverse('houses_hub:create_application', args=(house.id,)),
                                         {'students': json.dumps([])})
        self.assertEqual(post_response.status_code, 401)
        self.assertFalse(ApplicationInfo.objects.all().exists())
        self.assertFalse(Application.objects.all().exists())

    # Test that an agency gets 404 when trying to apply for a house
    def test_agency(self):
        house = create_house("Test house", 'Test agency')
        self.client.force_login(house.agency)
        response = self.client.get(reverse('houses_hub:create_application', args=(house.id,)))
        self.assertEquals(response.status_code, 403)
        post_response = self.client.post(reverse('houses_hub:create_application', args=(house.id,)),
                                         {'students': json.dumps([])})
        self.assertEqual(post_response.status_code, 403)
        self.assertFalse(ApplicationInfo.objects.all().exists())
        self.assertFalse(Application.objects.all().exists())

    # Test that an agent gets 404 when trying to apply for a house
    def test_agent(self):
        house = create_house("Test house", 'Test agency')
        agent = create_agent("Test agent", house.agency.username)
        self.client.force_login(agent)
        response = self.client.get(reverse('houses_hub:create_application', args=(house.id,)))
        self.assertEquals(response.status_code, 403)
        post_response = self.client.post(reverse('houses_hub:create_application', args=(house.id,)),
                                         {'students': json.dumps([])})
        self.assertEqual(post_response.status_code, 403)
        self.assertFalse(ApplicationInfo.objects.all().exists())
        self.assertFalse(Application.objects.all().exists())

    # Test that any student gets 200 when trying to apply for a house
    def test_any_student(self):
        house = create_house("Test house", 'Test agency')
        student = create_student("Test student")
        self.client.force_login(student)
        response = self.client.get(reverse('houses_hub:create_application', args=(house.id,)))
        self.assertEquals(response.status_code, 200)

    # Test that when a student applies alone for a house, an
    # Application is created with students empty and an application
    #  info belonging to that application and that student is created
    def test_student_applies_alone(self):
        house = create_house("Test house", 'Test agency')
        student = create_student("Test student")
        self.client.force_login(student)
        response = self.client.post(reverse('houses_hub:create_application', args=(house.id,)), {'students': json.dumps([])})
        self.assertEquals(response.status_code, 302)
        application = Application.objects.get(house=house)
        self.assertFalse(application.students.exists())
        self.assertFalse(application.submitted)
        self.assertEquals(application.house, house)
        application_info = ApplicationInfo.objects.get(student=student)
        self.assertEqual(application_info.student, student)
        self.assertEqual(application_info.application, application)

    # Test that when a student applies with 1 valid student
    # for a house, a Application is created with the student in students and an application
    #  info belonging to that application and that student is created
    def test_student_applies_with_one_student(self):
        house = create_house("Test house", 'Test agency')
        student = create_student("Test student")
        self.client.force_login(student)
        extra_student = create_student("Test student 2")
        extra_student.email = "test@test.com"
        # Must save student here to preserve email
        extra_student.save()
        response = self.client.post(reverse('houses_hub:create_application', args=(house.id,)),
                                    {'students': json.dumps(['test@test.com'])})
        self.assertEquals(response.status_code, 302)
        application = Application.objects.get(house=house)
        student_in_application = application.students.get(pk=extra_student.pk)
        self.assertEqual(student_in_application, extra_student)
        self.assertFalse(application.submitted)
        self.assertEquals(application.house, house)
        application_info = ApplicationInfo.objects.get(student=student)
        self.assertEqual(application_info.student, student)
        self.assertEqual(application_info.application, application)

    # Test that when a student applies
    # with multiple valid students for a house, a Application
    # is created with the multiple students in students and an application
    #  info belonging to that application and that student is created
    def test_student_applies_with_multiple_students(self):
        house = create_house("Test house", 'Test agency')
        student = create_student("Test student")
        self.client.force_login(student)
        first_extra_student = create_student("Test student 2")
        first_extra_student.email = "test2@test.com"
        # Must save student here to preserve email
        first_extra_student.save()
        second_extra_student = create_student("Test student 3")
        second_extra_student.email = "test3@test.com"
        # Must save student here to preserve email
        second_extra_student.save()
        response = self.client.post(reverse('houses_hub:create_application', args=(house.id,)),
                                    {'students': json.dumps(['test2@test.com', 'test3@test.com'])})
        self.assertEquals(response.status_code, 302)
        application = Application.objects.get(house=house)
        student_2_in_application = application.students.get(pk=first_extra_student.pk)
        student_3_in_application = application.students.get(pk=second_extra_student.pk)
        self.assertEqual(student_2_in_application, first_extra_student)
        self.assertEqual(student_3_in_application, second_extra_student)
        self.assertFalse(application.submitted)
        self.assertEquals(application.house, house)
        application_info = ApplicationInfo.objects.get(student=student)
        self.assertEqual(application_info.student, student)
        self.assertEqual(application_info.application, application)

    # Test that when a student applies with one non-existing
    # student for a house, Application is not created and 400 with error message is the response
    def test_student_applies_with_one_invalid_student(self):
        house = create_house("Test house", 'Test agency')
        student = create_student("Test student")
        self.client.force_login(student)
        extra_student = create_student("Test student 2")
        extra_student.email = "test2@test.com"
        # Must save student here to preserve email
        extra_student.save()
        response = self.client.post(reverse('houses_hub:create_application', args=(house.id,)),
                                    {'students': json.dumps(['invalidstudent@test.com'])})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data, {'response': ERROR_STUDENT_DOES_NOT_EXIST})
        self.assertFalse(Application.objects.all().exists())
        self.assertFalse(ApplicationInfo.objects.all().exists())

    # Test that when a student applies with multiple students where
    # some are invalid for a house, Application is not created and 400 with error message is the response
    def test_student_applies_with_multiple_invalid_students(self):
        house = create_house("Test house", 'Test agency')
        student = create_student("Test student")
        self.client.force_login(student)
        first_extra_student = create_student("Test student 2")
        first_extra_student.email = "test2@test.com"
        # Must save student here to preserve email
        first_extra_student.save()
        second_extra_student = create_student("Test student 3")
        second_extra_student.email = "test3@test.com"
        # Must save student here to preserve email
        second_extra_student.save()
        response = self.client.post(reverse('houses_hub:create_application', args=(house.id,)),
                                    {'students': json.dumps(['test2@test.com', 'invalidstudent@test.com'])})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data, {'response': ERROR_STUDENT_DOES_NOT_EXIST})
        self.assertFalse(Application.objects.all().exists())
        self.assertFalse(ApplicationInfo.objects.all().exists())

    # Test that when a student applies with multiple repeated students
    # Application is not created and 400 with error message is the response
    def test_student_applies_with_multiple_repeated_students(self):
        house = create_house("Test house", 'Test agency')
        student = create_student("Test student")
        self.client.force_login(student)
        first_extra_student = create_student("Test student 2")
        first_extra_student.email = "test2@test.com"
        # Must save student here to preserve email
        first_extra_student.save()
        response = self.client.post(reverse('houses_hub:create_application', args=(house.id,)),
                                    {'students': json.dumps(['test2@test.com', 'test2@test.com'])})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data, {'response': ERROR_REPEATED_STUDENT})
        self.assertFalse(Application.objects.all().exists())
        self.assertFalse(ApplicationInfo.objects.all().exists())

    # Test that when a student applies and puts it's own email in the application
    # Application is not created and 400 with error message is the response
    def test_student_applies_with_email_as_input(self):
        house = create_house("Test house", 'Test agency')
        student = create_student("Test student")
        student.email = "test@test.com"
        student.save()
        self.client.force_login(student)
        response = self.client.post(reverse('houses_hub:create_application', args=(house.id,)),
                                    {'students': json.dumps(['test@test.com'])})
        self.assertEquals(response.status_code, 400)
        self.assertEquals(response.data, {'response': ERROR_REPEATED_STUDENT})
        self.assertFalse(Application.objects.all().exists())
        self.assertFalse(ApplicationInfo.objects.all().exists())


class HousesIndexViewTests(TestCase):

    # Test that an anonymous user can access it 
    def test_not_logged_in_user(self):
        create_house("Test address", 'Test agency')
        response = self.client.get(reverse('houses_hub:index'))
        self.assertEqual(response.status_code, 200)

    # Test that an agency user can access it 
    def test_agency(self):
        house = create_house("Test address", 'Test agency')
        self.client.force_login(house.agency)
        response = self.client.get(reverse('houses_hub:index'))
        self.assertEqual(response.status_code, 200)

    # Test that a student can access it 
    def test_student(self):
        create_house("Test address", 'Test agency')
        student = create_student("Test student")
        self.client.force_login(student)
        response = self.client.get(reverse('houses_hub:index'))
        self.assertEqual(response.status_code, 200)

    # Test that an agent can access it 
    def test_agent(self):
        house = create_house("Test address", 'Test agency')
        agent = create_agent("Test agent", house.agency.username)
        self.client.force_login(agent)
        response = self.client.get(reverse('houses_hub:index'))
        self.assertEqual(response.status_code, 200)


class HouseDetailViewTests(TestCase):

    # Test anonymous user sees detail of a house without link to apply for the house 
    def test_not_logged_in_user(self):
        house = create_house("Test address", 'Test agency')
        response = self.client.get(reverse('houses_hub:detail', args=(house.id,)))
        self.assertEqual(response.status_code, 200)


    def test_agency(self):
        house = create_house("Test address", 'Test agency')
        self.client.force_login(house.agency)
        response = self.client.get(reverse('houses_hub:detail', args=(house.id,)))
        self.assertEqual(response.status_code, 200)


    def test_agent(self):
        house = create_house("Test address", 'Test agency')
        agent = create_agent("Test agent", house.agency.username)
        self.client.force_login(agent)
        response = self.client.get(reverse('houses_hub:detail', args=(house.id,)))
        self.assertEqual(response.status_code, 200)


    def test_student(self):
        house = create_house("Test address", 'Test agency')
        student = create_student("Test student")
        self.client.force_login(student)
        response = self.client.get(reverse('houses_hub:detail', args=(house.id,)))
        self.assertEqual(response.status_code, 200)


class HomeViewTests(TestCase):

    # Test a student with no lease and no applications
    # pending or open sees home page without fill applications house issues or accept applications
    # and sees its username 
    def test_student_without_lease_or_applications(self):
        student = create_student("Test student")
        self.client.force_login(student)
        response = self.client.post(reverse('houses_hub:home'), {'address': "woodward buildings"})
        self.assertEqual(response.status_code, 302)

    # Test a student with no a lease, open applications and pending applications sees all the links 
    # and sees its username 
    def test_student_all_fields(self):
        first_house = create_house("woodward buildings", 'test agency')
        coords: Coordinates = GAPI.extract_coordinates(first_house.address)
        first_house.lat = coords.latitude
        first_house.lgn = coords.longitude
        first_house.save()
        second_house = create_house('latymer court', 'Second test agency')
        coords: Coordinates = GAPI.extract_coordinates(second_house.address)
        second_house.lat = coords.latitude
        second_house.lgn = coords.longitude
        second_house.save()
        third_house = create_house('streatham hill', 'Third test agency')
        coords: Coordinates = GAPI.extract_coordinates(third_house.address)
        third_house.lat = coords.latitude
        third_house.lgn = coords.longitude
        third_house.save()
        student = create_student("Test student")
        create_application(house=first_house, submitted=False, extra_students=[student.id],
                           creator=create_student('Creator'), personal_details='TPD',
                           money='Test money', letter_of_recommendation='TLR')
        create_application(house=second_house, submitted=False,
                           extra_students=no_extra_students_dict['none'],
                           creator=student, personal_details='TPD', money='Test money',
                           letter_of_recommendation='TLR')
        lease = create_lease(third_house, expiration_date=timezone.now() + timedelta(days=30))
        student.lease.clear()
        student.lease.add(lease)
        # Must save student here to preserve the lease of the student
        student.save()
        self.client.force_login(student)
        response = self.client.post(reverse('houses_hub:home'), {'address': "woodward buildings"})
        self.assertEqual(response.status_code, 302)

    # Test anonymous user can't access home page (for now)
    def test_anonymous_user(self):
        response = self.client.post(reverse('houses_hub:home'), {'address': "woodward buildings"})
        self.assertEqual(response.status_code, 302)

    # Test agency can access home page and has a link to the
    # issues index for agencies, a link to its managed houses, and a link to create an agent
    def test_agency(self):
        house = create_house("woodward buildings", 'Test agency')
        coords: Coordinates = GAPI.extract_coordinates(house.address)
        house.lat = coords.latitude
        house.lgn = coords.longitude
        house.save()
        self.client.force_login(house.agency)
        response = self.client.post(reverse('houses_hub:home'), {'address': "woodward buildings"})
        self.assertEqual(response.status_code, 302)

from django.test import TestCase, Client
from rest_framework.test import APITestCase

from .models import CustomUser
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.urls import reverse
from .forms import *
from django.contrib import auth
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from .create_users import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.admin import UserAdmin


# Testing the USERS get created - Needed as we're using a custom user type and a custom backend
class CustomUserObjectTests(TestCase):
    # Testing a STUDENT gets created in the DB with the correct email and correct usertype
    def test_custom_user_student_gets_created(self):
        mail = "pypypy@pypypy.com"
        student = create_student(mail)
        from_db = CustomUser.objects.get(email=mail, usertype=CustomUser.USERTYPE_DICT['STUDENT'])
        self.assertTrue(student == from_db)
        self.assertTrue(student.usertype == CustomUser.USERTYPE_DICT['STUDENT'])

    # Testing an AGENCY gets created in the DB with the correct email and the correct usertype
    def test_custom_user_agency_gets_created(self):
        mail = "pypypy@pypypy.com"
        agency = create_agency(mail)
        from_db = CustomUser.objects.get(email=mail, usertype=CustomUser.USERTYPE_DICT['AGENCY'])
        self.assertTrue(agency == from_db)
        self.assertTrue(agency.usertype == CustomUser.USERTYPE_DICT['AGENCY'])


# Testing the LoginRegister FORM accepts fields as expected
class LoginRegisterFormTests(TestCase):

    # Checking form with correct data passes
    def test_valid_login_register_post_data(self):
        form = LoginRegisterForm(data={'email': "user@mp.com", 'password': "user"})
        self.assertTrue(form.is_valid())

    # Checking form with empty email gets rejected
    def test_invalid_login_register_post_data_no_email(self):
        form = LoginRegisterForm(data={'email': "", 'password': "user"})
        self.assertFalse(form.is_valid())

    # Checking form with empty password gets rejected
    def test_invalid_login_register_post_data_no_password(self):
        form = LoginRegisterForm(data={'email': "a@a.com", 'password': ""})
        self.assertFalse(form.is_valid())

    # Checking form with both fields empty gets rejected
    def test_invalid_login_register_post_data_no_email_no_password(self):
        form = LoginRegisterForm(data={'email': "", 'password': ""})
        self.assertFalse(form.is_valid())

    # Checking invalid email format gets rejected
    def test_invalid_login_register_post_data_invalid_email(self):
        form = LoginRegisterForm(data={'email': "albert", 'password': "user"})
        self.assertFalse(form.is_valid())

    # Checking empty data gets rejected
    def test_invalid_login_register_post_data_empty(self):
        form = LoginRegisterForm(data={})
        self.assertFalse(form.is_valid())

    # Checking missing password field gets rejected
    def test_invalid_login_register_post_data_no_password2(self):
        form = LoginRegisterForm(data={'email': "albert"})
        self.assertFalse(form.is_valid())

    # Checking missing email field gets rejected
    def test_invalid_login_register_post_data_no_email2(self):
        form = LoginRegisterForm(data={'password': "user"})
        self.assertFalse(form.is_valid())

    def test_invalid_login_register_post_data_more_fields(self):
        form = LoginRegisterForm(data={'email': "albert", 'password': "user", "abc": "abc"})
        self.assertFalse(form.is_valid())


# Testing the CreateSingleAgent FORM accepts fields as expected
class CreateSingleAgentFormTests(TestCase):
    # Correct form should pass
    def test_valid_create_single_agent_form(self):
        form = CreateSingleAgentForm(
            data={'email': "user@mp.com", 'password': "user", 'first_name': "Albert", 'last_name': "SurnameCool"})
        self.assertTrue(form.is_valid())

    # Checking form with empty email gets rejected
    def test_invalid_create_single_agent_form_no_email(self):
        form = CreateSingleAgentForm(
            data={'email': "", 'password': "user", 'first_name': "Albert", 'last_name': "SurnameCool"})
        self.assertFalse(form.is_valid())

    # Checking form with empty password gets rejected
    def test_invalid_create_single_agent_form_no_password(self):
        form = CreateSingleAgentForm(
            data={'email': "user@mp.com", 'password': "", 'first_name': "Albert", 'last_name': "SurnameCool"})
        self.assertFalse(form.is_valid())

    # Checking form with empty first name gets rejected
    def test_invalid_create_single_agent_form_no_first_name(self):
        form = CreateSingleAgentForm(
            data={'email': "user@mp.com", 'password': "user", 'first_name': "", 'last_name': "SurnameCool"})
        self.assertFalse(form.is_valid())

    # Checking form with empty last name gets rejected
    def test_invalid_create_single_agent_form_no_last_name(self):
        form = CreateSingleAgentForm(
            data={'email': "user@mp.com", 'password': "user", 'first_name': "Albert", 'last_name': ""})
        self.assertFalse(form.is_valid())

    # Checking form with invalid email gets rejected
    def test_invalid_create_single_agent_form_invalid_email(self):
        form = CreateSingleAgentForm(
            data={'email': "user", 'password': "user", 'first_name': "Albert", 'last_name': "SurnameCool"})
        self.assertFalse(form.is_valid())

    # Checking form with empty fields gets rejected
    def test_invalid_create_single_agent_form_empty(self):
        form = CreateSingleAgentForm(data={'email': "", 'password': "", 'first_name': '', 'last_name': ''})
        self.assertFalse(form.is_valid())

    # Checking form with no data gets rejected
    def test_invalid_create_single_agent_form_fields_missing_all(self):
        form = CreateSingleAgentForm(data={})
        self.assertFalse(form.is_valid())

    # Checking missing fields get rejected
    def test_invalid_create_single_agent_form_fields_missing_first_name(self):
        form = CreateSingleAgentForm(data={'email': "a@a.com", 'password': 'a', 'last_name': 'AnotherSurname'})
        self.assertFalse(form.is_valid())

    # Checking missing fields get rejected
    def test_invalid_create_single_agent_form_fields_missing_last_name(self):
        form = CreateSingleAgentForm(data={'email': "a@a.com", 'password': 'a', 'first_name': 'AnotherSurname'})
        self.assertFalse(form.is_valid())

    # Checking missing fields get rejected
    def test_invalid_create_single_agent_form_fields_missing_password(self):
        form = CreateSingleAgentForm(data={'email': "a@a.com", 'first_name': 'Vlad', 'first_name': 'AnotherSurname'})
        self.assertFalse(form.is_valid())

    # Checking missing fields get rejected
    def test_invalid_create_single_agent_form_fields_missing_email(self):
        form = CreateSingleAgentForm(data={'last_name': "Lol", 'password': 'a', 'first_name': 'AnotherSurname'})
        self.assertFalse(form.is_valid())

    def test_invalid_create_single_agent_form_more_data(self):
        form = CreateSingleAgentForm(
            data={'last_name': "Lol", 'password': 'a', 'first_name': 'AnotherSurname', 'email': 'a@a.coms', "lo": "abc"})
        self.assertTrue(form.is_valid())


class LoginViewTests(TestCase):
    # Checking a logged in STUDENT cannot access the login page nor can a logged in user submit POST to the login controller
    def test_logged_in_student(self):
        # Logged in STUDENTS should not be able to access login
        mail = "a@a.com"
        student = create_student(mail)
        self.client.force_login(student)
        get_response = self.client.get(reverse('login_register_service_hub:login'))
        self.assertEqual(get_response.status_code, 404)
        post_data = create_student_register_post_data(mail)
        post_response = self.client.post(reverse('login_register_service_hub:login'), post_data)
        self.assertEqual(post_response.status_code, 404)

    # Checking a logged in AGENCY cannot access the login page nor can a logged in user submit POST to the login controller
    def test_logged_in_agency(self):
        mail = "b@b.com"
        agency = create_agency(mail)
        self.client.force_login(agency)
        get_response = self.client.get(reverse('login_register_service_hub:login'))
        self.assertEqual(get_response.status_code, 404)
        post_data = create_student_register_post_data(mail)
        post_response = self.client.post(reverse('login_register_service_hub:login'), post_data)
        self.assertEqual(post_response.status_code, 404)

    # Checking a logged in AGENT cannot access the login page nor can a logged in user submit POST to the login controller
    def test_logged_in_agent(self):
        mail = "c@c.com"
        agent = create_agent_passing_agency(mail, create_agency("b@b.com"))
        self.client.force_login(agent)
        get_response = self.client.get(reverse('login_register_service_hub:login'))
        self.assertEqual(get_response.status_code, 404)
        post_data = create_student_register_post_data(mail)
        post_response = self.client.post(reverse('login_register_service_hub:login'), post_data)
        self.assertEqual(post_response.status_code, 404)

    # Anonymous user should be able to login
    # Note anonymous user being able to login must succeed as otherwise the tests above fail
    def test_anonymous_user(self):
        # Anonymous User should be able to login
        get_response = self.client.get(reverse('login_register_service_hub:login'))
        self.assertEqual(get_response.status_code, 200)
        # post_data = create_student_register_post_data(mail)
        # post_response = self.client.post(reverse('login_register_service_hub:login'), post_data)
        # self.assertEqual(post_response.status_code, 404)


class RegisterStudentViewTests(TestCase):
    # Logged in STUDENTS should not be able to access register nor able to submit POST to register controller
    def test_logged_in_student(self):
        mail = "a@a.com"
        student = create_student(mail)
        self.client.force_login(student)
        get_response = self.client.get(reverse('login_register_service_hub:register'))
        self.assertEqual(get_response.status_code, 404)
        post_data = create_student_register_post_data(mail)
        post_response = self.client.post(reverse('login_register_service_hub:register'), post_data)
        self.assertEqual(post_response.status_code, 404)

    # Logged in AGENCY should not be able to access register nor able to submit POST to register controller
    def test_logged_in_agency(self):
        mail = "a@a.com"
        agency = create_agency(mail)
        self.client.force_login(agency)
        get_response = self.client.get(reverse('login_register_service_hub:register'))
        self.assertEqual(get_response.status_code, 404)
        post_data = create_student_register_post_data(mail)
        post_response = self.client.post(reverse('login_register_service_hub:register'), post_data)
        self.assertEqual(post_response.status_code, 404)

    # Logged in AGENT should not be able to access register nor able to submit POST to register controller
    def test_logged_in_agent(self):
        mail = "c@c.com"
        agent = create_agent_passing_agency(mail, create_agency("b@b.com"))
        self.client.force_login(agent)
        get_response = self.client.get(reverse('login_register_service_hub:register'))
        self.assertEqual(get_response.status_code, 404)
        post_data = create_student_register_post_data(mail)
        post_response = self.client.post(reverse('login_register_service_hub:register'), post_data)
        self.assertEqual(post_response.status_code, 404)

    # Anonymous user can get access to registration and can register
    # 302 status code though. Can someone explain this please?
    def test_anonymous_user(self):
        get_response = self.client.get(reverse('login_register_service_hub:register'))
        self.assertEqual(get_response.status_code, 200)
        post_data = create_student_register_post_data("studentmail@studentmail.com")
        post_response = self.client.post(reverse('login_register_service_hub:register'), post_data)
        self.assertEqual(post_response.status_code, 302)


class CreateAgentViewTests(TestCase):

    # Logged in STUDENT should not be able to access the page to create an agent
    # Logged in STUDENT should not be able to POST to the page handling the creation of agents
    def test_logged_in_student(self):
        student = create_student("a@a.com")
        self.client.force_login(student)
        get_response = self.client.get(reverse('login_register_service_hub:create_agent'))
        self.assertEqual(get_response.status_code, 404)
        post_data = create_agent_register_post_data("agentmail@agentmail.com",
                                                    create_agency("hasntloggedin@hasntloggedin.com"))
        post_response = self.client.post(reverse('login_register_service_hub:create_agent'), post_data)
        self.assertEqual(post_response.status_code, 404)

    # Logged in AGENCY should be able to access the page handling creation of agents
    # Logged in AGENCY should also be able to POST to the page handling the creation of agents
    def test_logged_in_agency(self):
        agency = create_agency("b@b.com")
        self.client.force_login(agency)
        get_response = self.client.get(reverse('login_register_service_hub:create_agent'))
        self.assertEqual(get_response.status_code, 200)
        post_data = create_agent_register_post_data("agentmail@agentmail.com", agency)
        post_response = self.client.post(reverse('login_register_service_hub:create_agent'), post_data)
        self.assertEqual(post_response.status_code, 302)

    # Logged in AGENT should not be able to access the page handling the creation of agents
    # Logged in AGENT should not be able to POST to the page handling the creation of agents
    def test_logged_in_agent(self):
        self.agent = create_agent_passing_agency("c@c.com", create_agency("b@b.com"))
        self.client.force_login(self.agent)
        get_response = self.client.get(reverse('login_register_service_hub:create_agent'))
        self.assertEqual(get_response.status_code, 404)
        post_data = create_agent_register_post_data("agentmail@agentmail.com",
                                                    create_agency("hasntloggedin@hasntloggedin.com"))
        post_response = self.client.post(reverse('login_register_service_hub:create_agent'), post_data)
        self.assertEqual(post_response.status_code, 404)

    # Anonymous user should not be able to access the page handling the creation of agents
    # Anonymous user should not be able to POST to the controller handling the creation of agents
    def test_anonymous_user(self):
        get_response = self.client.get(reverse('login_register_service_hub:create_agent'))
        self.assertEqual(get_response.status_code, 404)
        post_data = create_agent_register_post_data("agentmail@agentmail.com",
                                                    create_agency("hasntloggedin@hasntloggedin.com"))
        post_response = self.client.post(reverse('login_register_service_hub:create_agent'), post_data)
        self.assertEqual(post_response.status_code, 404)


class CreateAgencyTests(TestCase):
    # Logged in STUDENT should not be able to access the page for creating agencies
    # Logged in STUDENT should not be able to POST to the controller handling the creation of agencies
    def test_logged_in_student(self):
        student = create_student("a@a.com")
        self.client.force_login(student)
        get_response = self.client.get(reverse('login_register_service_hub:create_agency'))
        self.assertEqual(get_response.status_code, 404)
        post_data = create_agency_register_post_data("dfgc@dfgc.com")
        post_response = self.client.post(reverse('login_register_service_hub:create_agency'), post_data)
        self.assertEqual(post_response.status_code, 404)

    # Logged in AGENCY should not be able to access the page for creating agencies
    # Logged in AGENCY should not be able to POST to the controller handling the creation of agencies
    def test_logged_in_agency(self):
        agency = create_agency("b@b.com")
        self.client.force_login(agency)
        get_response = self.client.get(reverse('login_register_service_hub:create_agency'))
        self.assertEqual(get_response.status_code, 404)
        post_data = create_agency_register_post_data("dfgc@dfgc.com")
        post_response = self.client.post(reverse('login_register_service_hub:create_agency'), post_data)
        self.assertEqual(post_response.status_code, 404)

    # Logged in AGENT should not be able to access the page for creating agencies
    # Logged in AGENT should not be able to POST to the controller handling the creation of agencies
    def test_logged_in_agent(self):
        # Logged in AGENT should not be able to create an agency
        agent = create_agent_passing_agency("c@c.com", create_agency("b@b.com"))
        self.client.force_login(agent)
        get_response = self.client.get(reverse('login_register_service_hub:create_agency'))
        self.assertEqual(get_response.status_code, 404)
        post_data = create_agency_register_post_data("dfgc@dfgc.com")
        post_response = self.client.post(reverse('login_register_service_hub:create_agency'), post_data)
        self.assertEqual(post_response.status_code, 404)

    # Anonymous user should be able to access the page for creating agencies
    # Anonymous uer should be able to POST to the controller for creating agencies
    def test_anonymous_user(self):
        get_response = self.client.get(reverse('login_register_service_hub:create_agency'))
        self.assertEqual(get_response.status_code, 200)
        post_data = create_agency_register_post_data("dfgc@dfgc.com")
        post_response = self.client.post(reverse('login_register_service_hub:create_agency'), post_data)
        self.assertEqual(post_response.status_code, 302)


class LogoutTests(TestCase):
    # Following operation should be valid
    # Logging in - Logging out - Logging in
    def test_register_logout_login(self):
        mail = "abcd@abcd.com"
        post_data = create_student_register_post_data(mail)
        response1 = self.client.post(reverse('login_register_service_hub:register'), post_data)
        response2 = self.client.get(reverse('login_register_service_hub:logout'))
        response3 = self.client.post(reverse('login_register_service_hub:login'), post_data)
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(response3.status_code, 302)

    # Registering a user with the same email should print username already registered but shouldn't fail from the server
    # Need to check the contents of the HTML returned
    def test_register_logout_register(self):
        mail = "abcd@abcd.com"
        data = create_student_register_post_data(mail)
        response1 = self.client.post(reverse('login_register_service_hub:register'), data)
        response2 = self.client.get(reverse('login_register_service_hub:logout'))
        response3 = self.client.post(reverse('login_register_service_hub:register'), data)
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(response3.status_code, 400)

    # A POST call after the agency logs out should fail if that call tries to register an agent
    def test_agency_logout_create_agent(self):
        agency_mail = "dfgc@dfgc.com"
        agency_data = create_agency_register_post_data(agency_mail)
        response1 = self.client.post(reverse('login_register_service_hub:create_agency'), agency_data)
        agent_data = create_agent_register_post_data("agentmail@agentmail.com",
                                                     CustomUser.objects.get(email=agency_mail))
        response2 = self.client.get(reverse('login_register_service_hub:logout'))
        response3 = self.client.post(reverse('login_register_service_hub:create_agent'), agent_data)
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(response3.status_code, 404)

    # What are the implications of logging out an anonymous user?
    def test_logout_when_anonymous(self):
        # Anonymous User can logout actually
        response = self.client.get(reverse('login_register_service_hub:logout'))
        self.assertEqual(response.status_code, 302)

    # def student_registers_twice(self):
    # Registered students shouldn't be able to register with same username"""


class PostTests(TestCase):
    # Creating a student works? - Don't we already have tests for this?
    def test_student_registers(self):
        mail = "abcd@abcd.com"
        post_data = create_student_register_post_data(mail)
        response = self.client.post(reverse('login_register_service_hub:register'), post_data)
        self.assertEqual(response.status_code, 302)  # check db changed
        self.assertEqual(CustomUser.objects.get(email=mail).email, post_data['email'])

    # Don't we have this already?
    def test_student_registers_twice(self):
        mail = "abcd@abcd.com"
        post_data = create_student_register_post_data(mail)
        response1 = self.client.post(reverse('login_register_service_hub:register'), post_data)
        response2 = self.client.post(reverse('login_register_service_hub:register'), post_data)
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(response2.status_code, 404)

    # Don't we have this already?
    def test_student_login_twice(self):
        # cannot login if ur logged in
        mail = "abcd@abcd.com"
        post_data = create_student_register_post_data(mail)
        self.client.post(reverse('login_register_service_hub:register'), post_data)
        response2 = self.client.post(reverse('login_register_service_hub:login'), post_data)
        self.assertEqual(response2.status_code, 404)

    # Don't we have this already?
    def test_post_create_agency(self):
        mail = "dfgc@dfgc.com"
        post_data = create_agency_register_post_data(mail)
        response = self.client.post(reverse('login_register_service_hub:create_agency'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CustomUser.objects.get(email=mail, usertype=CustomUser.USERTYPE_DICT['AGENCY']).email,
                         mail)

    # Don't we have this already?
    def test_post_create_agent(self):
        mail = "abcd@abcd.com"
        agency_mail = "dfgc@dfgc.com"
        agency = create_agency(agency_mail)
        self.client.force_login(agency)
        post_data = create_agent_register_post_data(mail, agency)
        response = self.client.post(reverse('login_register_service_hub:create_agent'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CustomUser.objects.get(email=mail, usertype=CustomUser.USERTYPE_DICT['SINGLE_AGENT']).email,
                         mail)

    # Don't we have this already?
    def test_post_create_student_big_form(self):
        # cannot login if ur logged in
        mail = "danigr.99727.com"
        post_data = create_student_register_post_data(mail)
        post_data = post_data.update({"extraField": "i shouldn't exist"})
        response = self.client.post(reverse('login_register_service_hub:register'), post_data)
        self.assertEqual(response.status_code, 400)

    def test_post_create_agent_big_form(self):
        mail = "abcd@abcd.com"
        agency_mail = "dfgc@dfgc.com"
        self.client.force_login(create_agency(agency_mail))
        post_data = create_agent_register_post_data(mail, agency_mail)
        post_data = post_data.update({"extraField": "i shouldn't exist"})
        response = self.client.post(reverse('login_register_service_hub:create_agent'), post_data)
        self.assertEqual(response.status_code, 400)

    def test_agency_create_agent_twice(self):
        agency_mail = "dfgc@dfgc.com"
        agency_data = create_agency_register_post_data(agency_mail)
        response1 = self.client.post(reverse('login_register_service_hub:create_agency'), agency_data)
        agent_data = create_agent_register_post_data("agentmail@agentmail.com",
                                                     CustomUser.objects.get(email=agency_mail))
        response2 = self.client.post(reverse('login_register_service_hub:create_agent'), agent_data)
        response3 = self.client.post(reverse('login_register_service_hub:create_agent'), agent_data)
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(response2.status_code, 302)
        self.assertEqual(response3.status_code, 400)


class APIRegisterLoginTests(APITestCase):

    def test_anonymous_user_can_register_student(self):
        response = self.client.post(reverse("login_register_service_hub:api-register-student"),
                                    data={'username': "vlad", 'password': 'abc123', 'email': "vlad@vlad.com"})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CustomUser.objects.filter(username="vlad", email="vlad@vlad.com", usertype=1).exists())

    def test_registered_student_can_login(self):
        email = "vlad@vlad.com"
        password = "abc123"
        username = "vlad"
        response = self.client.post(reverse("login_register_service_hub:api-register-student"),
                                    data={'username': username, 'password': password, 'email': email})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CustomUser.objects.filter(username=username, email=email, usertype=1).exists())
        self.assertFalse(CustomUser.objects.filter(usertype=2).exists())
        login_response = self.client.post(reverse("login_register_service_hub:api-login"),
                                          data={'username': email, 'password': password})
        self.assertEqual(login_response.status_code, 200)

    def test_logged_in_student_cannot_register_student(self):
        student = create_student("vlad@vlad.com")
        self.client.force_login(student)
        response = self.client.post(reverse("login_register_service_hub:api-register-student"),
                                    data={'username': "vladAnotherSurname", 'password': 'abc123',
                                          'email': "vladAnotherSurname@vlad.com"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(CustomUser.objects.filter(username="vladAnotherSurname", email="vladAnotherSurname@vlad.com").exists())

    def test_logged_in_agency_cannot_register_student(self):
        agency = create_agency("someagency@someagency.com")
        self.client.force_login(agency)
        response = self.client.post(reverse("login_register_service_hub:api-register-student"),
                                    data={'username': "vladAnotherSurname", 'password': 'abc123',
                                          'email': "vladAnotherSurname@vlad.com"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(CustomUser.objects.filter(username="vladAnotherSurname", email="vladAnotherSurname@vlad.com").exists())

    def test_anonymous_user_can_register_agency(self):
        response = self.client.post(reverse("login_register_service_hub:api-register-agency"),
                                    data={'username': "vlad", 'password': 'abc123', 'email': "vlad@vlad.com"})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CustomUser.objects.filter(username="vlad", email="vlad@vlad.com", usertype=2).exists())
        self.assertFalse(CustomUser.objects.filter(usertype=1).exists())

    def test_registered_agency_can_login(self):
        email = "vlad@vlad.com"
        password = "abc123"
        username = "vlad"
        response = self.client.post(reverse("login_register_service_hub:api-register-agency"),
                                    data={'username': username, 'password': password, 'email': email})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(CustomUser.objects.filter(username=username, email=email, usertype=2).exists())
        self.assertFalse(CustomUser.objects.filter(usertype=1).exists())
        login_response = self.client.post(reverse("login_register_service_hub:api-login"),
                                          data={'username': email, 'password': password})
        self.assertEqual(login_response.status_code, 200)

    def test_logged_in_agency_cannot_register_agency(self):
        agency = create_agency("someagency@someagency.com")
        self.client.force_login(agency)
        response = self.client.post(reverse("login_register_service_hub:api-register-agency"),
                                    data={'username': "vladAnotherSurname", 'password': 'abc123',
                                          'email': "vladAnotherSurname@vlad.com"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(CustomUser.objects.filter(username="vladAnotherSurname", email="vladAnotherSurname@vlad.com").exists())

    def test_logged_in_student_cannot_register_agency(self):
        student = create_student("vlad@vlad.com")
        self.client.force_login(student)
        response = self.client.post(reverse("login_register_service_hub:api-register-agency"),
                                    data={'username': "vladAnotherSurname", 'password': 'abc123',
                                          'email': "vladAnotherSurname@vlad.com"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(CustomUser.objects.filter(username="vladAnotherSurname", email="vladAnotherSurname@vlad.com").exists())

    def test_anonymous_user_cannot_register_student_without_email(self):
        response = self.client.post(reverse("login_register_service_hub:api-register-student"),
                                    data={'username': "vlad", 'password': 'abc123'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(CustomUser.objects.filter(usertype=1).exists())

    def test_anonymous_user_cannot_register_student_without_username(self):
        response = self.client.post(reverse("login_register_service_hub:api-register-student"),
                                    data={'email': "vlad@vlad.com", 'password': 'abc123'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(CustomUser.objects.filter(usertype=1).exists())

    def test_anonymous_user_cannot_register_student_without_password(self):
        response = self.client.post(reverse("login_register_service_hub:api-register-student"),
                                    data={'email': "vlad@vlad.com", 'username': 'vlad'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(CustomUser.objects.filter(usertype=1).exists())

    def test_anonymous_user_cannot_register_student_with_same_username(self):
        user = create_student("vlad@vlad.com")
        response = self.client.post(reverse("login_register_service_hub:api-register-student"),
                                    data={'email': "albert@albert.com", 'username': 'vlad'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(CustomUser.objects.filter(email="albert@albert.com").exists())

    def test_anonymous_user_cannot_register_student_with_same_email(self):
        user = create_student("vlad@vlad.com")
        response = self.client.post(reverse("login_register_service_hub:api-register-student"),
                                    data={'email': "vlad@vlad.com", 'username': 'albert'})
        self.assertEqual(response.status_code, 400)
        self.assertFalse(CustomUser.objects.filter(username="albert").exists())

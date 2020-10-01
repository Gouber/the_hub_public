from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.utils import json

from .forms import *
from django.urls import reverse
from .models import Issue, Message

# Creating functions
from login_register_service_hub.create_users import *
from houses_hub.create_houses import *
from issues.create_issues import *

# Note that when you create an issue you must automatically generate the message associated with it
# This message belongs to a user
# Also note that the issue itself belongs to a house
from .serializers import MessageListSerializer


class FormsTests(TestCase):

    def test_create_issue_form_valid(self):
        form = CreateIssueForm(data={'title': "Problem with heating", 'text': "The heating doesn't work at night"})
        self.assertTrue(form.is_valid())

    def test_create_issue_form_no_title(self):
        form = CreateIssueForm(data={'title': "", 'text': "The heating doesn't work at night"})
        self.assertFalse(form.is_valid())

    def test_create_issue_form_no_text(self):
        form = CreateIssueForm(data={'title': "Problem with heating", 'text': ""})
        self.assertFalse(form.is_valid())

    def test_message_form_valid(self):
        form = MessageForm(data={'text': "I will fix it tomorrow"})
        self.assertTrue(form.is_valid())

    def test_message_form_no_text(self):
        form = MessageForm(data={'test': ""})
        self.assertFalse(form.is_valid())


class APIIssuesTests(APITestCase):

    # all issues created here are by default not hidden so everyone should see them
    def test_anyone_can_access_issue_index_view_for_non_hidden_issues(self):
        agency = create_agency("someagency@someageny.com")
        house = create_house("Testing House", agency)
        user = create_student_with_lease("vlad@vlad.com", house)
        create_issue("No Water", "Where is the water", user, house)
        create_issue("Wow", "Just wow", user, house)
        response = self.client.get(reverse("issues:api-issue-index", args=(house.id,)))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Water")
        self.assertContains(response, "Wow")

        self.client.force_login(user)

        response = self.client.get(reverse("issues:api-issue-index", args=(house.id,)))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Water")
        self.assertContains(response, "Wow")

        self.client.force_login(agency)

        response = self.client.get(reverse("issues:api-issue-index", args=(house.id,)))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No Water")
        self.assertContains(response, "Wow")

    def test_hidden_issues_are_only_seen_by_users_with_lease_on_house_and_by_agency_users_owning_house(self):
        agency = create_agency("someagency@someageny.com")
        bad_agency = create_agency("anotheragency@anotheragency.com")
        house = create_house("Testing House", agency)
        different_house = create_house("Different House", agency)
        user = create_student_with_lease("vlad@vlad.com", house)
        bad_user = create_student("albert@albert.com")
        bad_user_with_lease = create_student_with_lease("dani@dani.com", different_house)

        # creating 1 visible issue and 1 hidden issue
        create_issue("No water", "Where is the water", user, house, hidden=True)
        create_issue("Bad Smell", "Where is this bad smell coming from", user, house)

        # anonymous user cannot see hidden issues
        response = self.client.get(reverse("issues:api-issue-index", args=(house.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No water")
        self.assertNotContains(response, "\"id\":1")
        self.assertContains(response, "Bad Smell")
        self.assertContains(response, "\"id\":2")

        # agency that doesn't own the house does not see the hidden issues
        self.client.force_login(bad_agency)
        response = self.client.get(reverse("issues:api-issue-index", args=(house.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No water")
        self.assertNotContains(response, "\"id\":1")
        self.assertContains(response, "Bad Smell")
        self.assertContains(response, "\"id\":2")
        self.client.logout()

        # student that doesn't have a lease AT ALL does not see the hidden issues
        self.client.force_login(bad_user)
        response = self.client.get(reverse("issues:api-issue-index", args=(house.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No water")
        self.assertNotContains(response, "\"id\":1")
        self.assertContains(response, "Bad Smell")
        self.assertContains(response, "\"id\":2")
        self.client.logout()

        # student that doesn't have a lease WITH THIS HOUSE does not see the hidden issues
        self.client.force_login(bad_user_with_lease)
        response = self.client.get(reverse("issues:api-issue-index", args=(house.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "No water")
        self.assertNotContains(response, "\"id\":1")
        self.assertContains(response, "Bad Smell")
        self.assertContains(response, "\"id\":2")
        self.client.logout()

        # student that has a lease with this house can see the hidden issues
        self.client.force_login(user)
        response = self.client.get(reverse("issues:api-issue-index", args=(house.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No water")
        self.assertContains(response, "\"id\":1")
        self.assertContains(response, "Bad Smell")
        self.assertContains(response, "\"id\":2")
        self.client.logout()

        # agency that owns this house can see the hidden issues
        self.client.force_login(agency)
        response = self.client.get(reverse("issues:api-issue-index", args=(house.id,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No water")
        self.assertContains(response, "\"id\":1")
        self.assertContains(response, "Bad Smell")
        self.assertContains(response, "\"id\":2")

    def test_user_with_lease_can_create_issues(self):
        # with perfect data
        house = create_house("Test House", create_agency("someagency@someageny.com"))
        user = create_student_with_lease("vlad@vlad.com", house)
        self.client.force_login(user)
        # CREATE HIDDEN ISSUE
        post = json.dumps({"title": "No Water", "hidden": "True",
                           "message": "Where is the water?"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)

        # CREATE VISIBLE ISSUE
        post = json.dumps({"title": "Big Issue",
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertEqual(response.status_code, 201)

        # CHECK HIDDEN ISSUE IS IN THE DB
        self.assertTrue(Message.objects.filter(issue=1, text="Where is the water?").exists())
        self.assertTrue(Issue.objects.filter(title="No Water", house=house).exists())
        self.assertEqual(Issue.objects.get(pk=1).get_creator(), user)

        # CHECK VISIBLE ISSUE IS IN THE DB
        self.assertTrue(Message.objects.filter(issue=2, text="Some sensible message here").exists())
        self.assertTrue(Issue.objects.filter(title="Big Issue", house=house).exists())
        self.assertEqual(Issue.objects.get(pk=2).get_creator(), user)

        # check that the issue index of this house contains this BOTH issues as we are currently signed in
        response = self.client.get(reverse("issues:api-issue-index", args=(house.id,)))
        self.assertContains(response, "Big Issue")
        self.assertContains(response, "\"id\":2")
        self.assertContains(response, "No Water")
        self.assertContains(response, "\"id\":1")

        # check that if you logout you can only see the non-hidden issue
        self.client.logout()
        response = self.client.get(reverse("issues:api-issue-index", args=(house.id,)))
        self.assertContains(response, "Big Issue")
        self.assertContains(response, "\"id\":2")
        self.assertNotContains(response, "No Water")
        self.assertNotContains(response, "\"id\":1")
        # LOG BACK IN
        self.client.force_login(user)

        # CHECK MESSAGE INDEX OF NON-HIDDEN-ISSUE
        response = self.client.get(reverse("issues:api-issue-chat", args=(2,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "\"sender\":{}".format(user.id))
        self.assertContains(response, "\"text\":\"Some sensible message here\"")

        # CHECK MESSAGE INDEX OF HIDDEN-ISSUE
        response = self.client.get(reverse("issues:api-issue-chat", args=(1,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "\"sender\":{}".format(user.id))
        self.assertContains(response, "\"text\":\"Where is the water?\"")

        # LOG OUT TO CHECK MESSAGE INDEX OF HIDDEN AND NON-HIDDEN ISSUES
        self.client.logout()

        # NON-HIDDEN-ISSUE SHOULD WORK
        response = self.client.get(reverse("issues:api-issue-chat", args=(2,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "\"sender\":{}".format(user.id))
        self.assertContains(response, "\"text\":\"Some sensible message here\"")

        # HIDDEN ISSUE SHOULD THROW 404
        response = self.client.get(reverse("issues:api-issue-chat", args=(1,)))
        self.assertEqual(response.status_code, 404)

    # Data will be overriden after we access the view rejecting bad behaviour
    def test_random_data_being_passed_in_json_creating_issue_is_ignored(self):
        house = create_house("Test House", create_agency("someagency@someageny.com"))
        user = create_student_with_lease("vlad@vlad.com", house)
        self.client.force_login(user)
        # CREATE HIDDEN ISSUE
        post = json.dumps({"title": "No Water", "hidden": "True", "user": 21, "house": 10, "houseid": house.id,
                           "message": "Where is the water?"}, indent=4, sort_keys=True, default=str)
        self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                         content_type="application/json")

        issue = Issue.objects.get(title="No Water")
        msg = Message.objects.get(text="Where is the water?")
        self.assertTrue(issue.house == house)
        self.assertTrue(msg.sender == user)

    def test_user_with_lease_can_create_hidden_issues(self):
        house = create_house("Test House", create_agency("someagency@someageny.com"))
        user = create_student_with_lease("vlad@vlad.com", house)
        self.client.force_login(user)
        post = json.dumps({"title": "Big Issue Not Hidden", "houseid": house.id,
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        post = json.dumps({"title": "Big Issue Hidden", 'hidden': "True", "houseid": house.id,
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.client.logout()
        response = self.client.get(reverse("issues:api-issue-index", args=(house.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Big Issue Not Hidden")
        self.assertContains(response, "\"id\":1")
        self.assertNotContains(response, "Big Issue Hidden")
        self.assertNotContains(response, "\"id\":2")
        self.client.force_login(user)
        response = self.client.get(reverse("issues:api-issue-index", args=(house.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Big Issue Not Hidden")
        self.assertContains(response, "\"id\":1")
        self.assertContains(response, "Big Issue Hidden")
        self.assertContains(response, "\"id\":2")
        another_user = create_student_with_lease("amy@amy.com", house)
        self.client.force_login(another_user)
        post = json.dumps({"title": "Another issue that is hidden", 'hidden': "True", "houseid": house.id,
                               "message": "Wow much issue"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(reverse("issues:api-issue-index", args=(house.id,)))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "Big Issue Not Hidden")
        self.assertContains(response, "\"id\":1")
        self.assertContains(response, "Big Issue Hidden")
        self.assertContains(response, "\"id\":2")
        self.assertContains(response, "Another issue that is hidden")
        self.assertContains(response, "\"id\":3")



    def test_anonymous_user_cannot_create_issue(self):
        # with perfect data
        house = create_house("test1", create_agency("agency@agency.com"))

        post = json.dumps({"title": "Big Issue Not Hidden",
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # passing random house
        post = json.dumps({"title": "Big Issue Not Hidden", "house": 21,
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # passing random user
        post = json.dumps({"title": "Big Issue Not Hidden", "user": 1,
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # random date
        post = json.dumps({"title": "Big Issue Not Hidden", "pub_date": timezone.now() + timezone.timedelta(days=1),
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # nothing has been created
        self.assertTrue(not Issue.objects.all().exists())

    def test_agency_user_cannot_create_issue(self):
        agency = create_agency("someagency@someageny.com")
        self.client.force_login(agency)
        # with perfect data
        post = json.dumps({"title": "Big Issue Not Hidden",
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(1,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # passing random house
        post = json.dumps({"title": "Big Issue Not Hidden", "house": 21,
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(1,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # passing random user
        post = json.dumps({"title": "Big Issue Not Hidden", "user": 1,
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(1,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # random date
        post = json.dumps({"title": "Big Issue Not Hidden", "pub_date": timezone.now() + timezone.timedelta(days=1),
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(1,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # nothing has been created
        self.assertTrue(not Issue.objects.all().exists())

    def test_agent_user_cannot_create_issue(self):
        agent = create_agent_passing_agency("agent@agent.com", create_agency("someagency@someageny.com"))
        house = create_house("test1", create_agency("agency@agency.com"))
        self.client.force_login(agent)
        # with perfect data
        post = json.dumps({"title": "Big Issue Not Hidden",
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # passing random house
        post = json.dumps({"title": "Big Issue Not Hidden", "house": 21,
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # passing random user
        post = json.dumps({"title": "Big Issue Not Hidden", "user": 1,
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # random date
        post = json.dumps({"title": "Big Issue Not Hidden", "pub_date": timezone.now() + timezone.timedelta(days=1),
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # nothing has been created
        self.assertTrue(not Issue.objects.all().exists())

    def test_student_without_lease_user_cannot_create_issue(self):
        student = create_student("vlad@vlad.com")
        house = create_house("test1", create_agency("agency@agency.com"))
        self.client.force_login(student)
        # with perfect data
        post = json.dumps({"title": "Big Issue Not Hidden",
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # passing random house
        post = json.dumps({"title": "Big Issue Not Hidden", "house": 21,
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # passing random user
        post = json.dumps({"title": "Big Issue Not Hidden", "user": 1,
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # random date
        post = json.dumps({"title": "Big Issue Not Hidden", "pub_date": timezone.now() + timezone.timedelta(days=1),
                           "message": "Some sensible message here"}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create", args=(house.id,)), data=post,
                                    content_type="application/json")
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # nothing has been created
        self.assertTrue(not Issue.objects.all().exists())

    def test_chat_of_hidden_issue_raises_404_for_anyone_but_correct_users(self):
        agency = create_agency("someagency@someageny.com")
        house = create_house("Test House", agency)
        user = create_student_with_lease("vlad@vlad.com", house)
        another_user = create_student_with_lease("amy@amy.com", house)
        create_issue("No water", "Where is the water", user, house, hidden=True)
        issue = Issue.objects.get(pk=1)
        issue.hidden = True
        issue.save()
        response = self.client.get(reverse("issues:api-issue-chat", args=(issue.id,)))
        self.assertTrue(response.status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_login(agency)
        response = self.client.get(reverse("issues:api-issue-chat", args=(issue.id,)))
        self.assertTrue(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "\"sender\":{}".format(user.id))
        self.assertContains(response, "\"text\":\"{}\"".format("Where is the water"))
        self.client.logout()
        response = self.client.get(reverse("issues:api-issue-chat", args=(issue.id,)))
        self.assertTrue(response.status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_login(user)
        response = self.client.get(reverse("issues:api-issue-chat", args=(issue.id,)))
        self.assertTrue(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "\"sender\":{}".format(user.id))
        self.assertContains(response, "\"text\":\"{}\"".format("Where is the water"))
        self.client.force_login(another_user)
        response = self.client.get(reverse("issues:api-issue-chat", args=(issue.id,)))
        self.assertTrue(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "\"sender\":{}".format(user.id))
        self.assertContains(response, "\"text\":\"{}\"".format("Where is the water"))


    def test_chat_for_issues_shows_all_messages(self):
        agency = create_agency("someagency@someageny.com")
        house = create_house("Test House", agency)
        user = create_student_with_lease("vlad@vlad.com", house)
        create_issue("No water", "Where is the water", user, house)
        issue = Issue.objects.get(pk=1)
        Message.objects.create(text="Why do you need water", sender=agency, issue=issue, date_sent=timezone.now())
        Message.objects.create(text="To throw water balloons at neighbour", sender=user, issue=issue,
                               date_sent=timezone.now())
        Message.objects.create(text="Is that legal?", sender=agency, issue=issue, date_sent=timezone.now())
        Message.objects.create(text="Fuck you", sender=user, issue=issue, date_sent=timezone.now())
        Message.objects.create(text="A", sender=agency, issue=issue, date_sent=timezone.now())
        Message.objects.create(text="B", sender=agency, issue=issue, date_sent=timezone.now())

        response = self.client.get(reverse("issues:api-issue-chat", args=(issue.id,)))
        msg_ser = MessageListSerializer(data=json.loads(response.content), many=True)
        if (msg_ser.is_valid()):
            self.assertTrue(len(msg_ser.validated_data) == 7)
            self.assertTrue(msg_ser.validated_data[0]["text"] == "Where is the water")
        else:
            # some behaviour must've changed to get here
            print(msg_ser.errors)
            self.assertTrue(False)

    def test_chat_for_issues_shows_all_messages_hidden_issue(self):
        agency = create_agency("someagency@someageny.com")
        house = create_house("Test House", agency)
        user = create_student_with_lease("vlad@vlad.com", house)
        create_issue("No water", "Where is the water", user, house, hidden=True)
        issue = Issue.objects.get(pk=1)
        Message.objects.create(text="Why do you need water", sender=agency, issue=issue, date_sent=timezone.now())
        Message.objects.create(text="To drink", sender=user, issue=issue,
                               date_sent=timezone.now())
        Message.objects.create(text="More Text", sender=agency, issue=issue, date_sent=timezone.now())
        Message.objects.create(text="Even More additional text", sender=user, issue=issue, date_sent=timezone.now())
        Message.objects.create(text="A", sender=agency, issue=issue, date_sent=timezone.now())
        Message.objects.create(text="B", sender=agency, issue=issue, date_sent=timezone.now())

        response = self.client.get(reverse("issues:api-issue-chat", args=(issue.id,)))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_login(agency)
        response = self.client.get(reverse("issues:api-issue-chat", args=(issue.id,)))
        msg_ser = MessageListSerializer(data=json.loads(response.content), many=True)
        if (msg_ser.is_valid()):
            self.assertTrue(len(msg_ser.validated_data) == 7)
            self.assertTrue(msg_ser.validated_data[0]["text"] == "Where is the water")
        else:
            # some behaviour must've changed to get here
            print(msg_ser.errors)
            self.assertTrue(False)

        self.client.logout()
        response = self.client.get(reverse("issues:api-issue-chat", args=(issue.id,)))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.client.force_login(user)

        response = self.client.get(reverse("issues:api-issue-chat", args=(issue.id,)))
        msg_ser = MessageListSerializer(data=json.loads(response.content), many=True)
        if (msg_ser.is_valid()):
            self.assertTrue(len(msg_ser.validated_data) == 7)
            self.assertTrue(msg_ser.validated_data[0]["text"] == "Where is the water")
        else:
            # some behaviour must've changed to get here
            print(msg_ser.errors)
            self.assertTrue(False)

    def test_student_with_lease_can_create_chat(self):
        agency = create_agency("someagency@someageny.com")
        house = create_house("Test House", agency)
        user = create_student_with_lease("vlad@vlad.com", house)
        issue_id = create_issue("No water", "Where is the water", user, house, hidden=True)
        post = json.dumps({"text": "I have now fixed the water",
                           "date_sent": timezone.now()}, indent=4, sort_keys=True, default=str)
        self.client.force_login(user)
        response = self.client.post(reverse("issues:api-issue-create-chat", args=(issue_id,)), data=post,
                                    content_type="application/json")
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Message.objects.filter(text="I have now fixed the water", sender=user,
                                               issue=Issue.objects.get(pk=issue_id)).exists())

    def test_student_with_lease_can_create_chat_additional_overriding_data(self):
        agency = create_agency("someagency@someageny.com")
        house = create_house("Test House", agency)
        bad_user = create_student("albert@albert.com")
        user = create_student_with_lease("vlad@vlad.com", house)
        issue_id = create_issue("No water", "Where is the water", user, house, hidden=True)
        post = json.dumps({"text": "I have now fixed the water", "sender": bad_user,
                           "date_sent": timezone.now()}, indent=4, sort_keys=True, default=str)
        self.client.force_login(user)
        response = self.client.post(reverse("issues:api-issue-create-chat", args=(issue_id,)), data=post,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Message.objects.filter(text="I have now fixed the water", sender=user,
                                               issue=Issue.objects.get(pk=issue_id)).exists())

    def test_student_with_lease_cannot_create_chat_for_other_issues_from_other_houses(self):
        agency = create_agency("someagency@someageny.com")
        house = create_house("Test House", agency)
        another_house = create_house("Another testing house", agency)
        albert_user = create_student_with_lease("albert@albert.com", another_house)
        vlad_user = create_student_with_lease("vlad@vlad.com", house)

        issue_vlad = create_issue("No water", "Where is the water", vlad_user, house, )
        issue_albert = create_issue("No heating", "Where is the heating", albert_user, another_house, )

        self.client.force_login(albert_user)

        post = json.dumps({"text": "I have now fixed the water", "user": vlad_user,
                           "date_sent": timezone.now()}, indent=4, sort_keys=True, default=str)
        response = self.client.post(reverse("issues:api-issue-create-chat", args=(issue_vlad,)), data=post,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.post(reverse("issues:api-issue-create-chat", args=(21,)), data=post,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.post(reverse("issues:api-issue-create-chat", args=(issue_albert,)), data=post,
                                    content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Message.objects.filter(text="I have now fixed the water", sender=albert_user).exists())

        response = self.client.get(reverse("issues:api-issue-chat", args=(issue_vlad,)))
        msg_ser = MessageListSerializer(data=json.loads(response.content), many=True)
        if (msg_ser.is_valid()):
            self.assertTrue(len(msg_ser.validated_data) == 1)
            self.assertTrue(msg_ser.validated_data[0]["text"] == "Where is the water")
        else:
            # some behaviour must've changed to get here
            print(msg_ser.errors)
            self.assertTrue(False)

        response = self.client.get(reverse("issues:api-issue-chat", args=(issue_albert,)))
        msg_ser = MessageListSerializer(data=json.loads(response.content), many=True)
        if (msg_ser.is_valid()):
            self.assertTrue(len(msg_ser.validated_data) == 2)
            self.assertTrue(msg_ser.validated_data[0]["text"] == "Where is the heating")
        else:
            # some behaviour must've changed to get here
            print(msg_ser.errors)
            self.assertTrue(False)

    def test_student_with_lease_can_close_issue_from_his_house(self):

        agency = create_agency("someagency@someageny.com")
        house = create_house("Test House", agency)
        user = create_student_with_lease("vlad@vlad.com", house)
        issue = create_issue("No water", "Where is the water", user, house, )
        self.assertTrue(Issue.objects.get(pk=1).closed == False)
        self.client.force_login(user)
        response = self.client.get(reverse("issues:api-issue-close-chat", args=(1,)))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(Issue.objects.get(pk=1).closed == True)

    def test_student_with_lease_can_close_issue_from_his_house_but_issue_created_by_another_User(self):
        agency = create_agency("someagency@someageny.com")
        house = create_house("Test House", agency)
        user = create_student_with_lease("vlad@vlad.com", house)
        another_user = create_student_with_lease("amy@amy.com", house)
        create_issue("No water", "Where is the water", user, house, )
        self.assertTrue(Issue.objects.get(pk=1).closed == False)
        self.client.force_login(another_user)
        response = self.client.get(reverse("issues:api-issue-close-chat", args=(1,)))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(Issue.objects.get(pk=1).closed == True)

    def test_student_with_lease_cannot_close_issue_from_another_house(self):
        agency = create_agency("someagency@someageny.com")
        big_house = create_house("Test House", agency)
        small_house = create_house("Another Test House", agency)

        user_one = create_student_with_lease("vlad@vlad.com", big_house)
        user_two = create_student_with_lease("albert@albert.com", small_house)

        issue_user_one = create_issue("No water", "Where is the water", user_one, big_house, )
        issue_user_two = create_issue("I need food", "Food is in high demand", user_two, small_house, )

        self.assertTrue(Issue.objects.get(pk=2).closed == False)
        self.client.force_login(user_one)
        response = self.client.get(reverse("issues:api-issue-close-chat", args=(issue_user_two,)))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Issue.objects.get(pk=2).closed == False)

        self.client.force_login(user_two)
        response = self.client.get(reverse("issues:api-issue-close-chat", args=(issue_user_two,)))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertTrue(Issue.objects.get(pk=2).closed == True)

    def test_student_without_lease_cannot_close_issue_from_another_house(self):
        house = create_house("Testing House", create_agency("someagency@someageny.com"))
        vlad = create_student_with_lease("vlad@vlad.com", house)
        albert = create_student("albert@albert.com")
        issue = create_issue("No Water", "Where is the water", vlad, house)
        self.assertTrue(Issue.objects.get(pk=1).closed == False)
        self.client.force_login(albert)
        response = self.client.get(reverse("issues:api-issue-close-chat", args=(issue,)))
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Issue.objects.get(pk=1).closed == False)

    def test_agency_owning_house_with_issue_cannot_close_said_issue(self):
        agency = create_agency("someagency@someageny.com")
        house = create_house("Testing House", agency)
        vlad = create_student_with_lease("vlad@vlad.com", house)
        issue = create_issue("No Water", "Where is the water", vlad, house)
        self.assertTrue(Issue.objects.get(pk=1).closed == False)
        self.client.force_login(agency)
        response = self.client.get(reverse("issues:api-issue-close-chat", args=(issue,)))
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Issue.objects.get(pk=1).closed == False)

    def test_random_agency_cannot_close_issue_from_another_house_owned_by_different_agency(self):
        bad_agency = create_agency("anotheragency@anotheragency.com")
        agency = create_agency("someagency@someageny.com")
        house = create_house("Testing House", agency)
        vlad = create_student_with_lease("vlad@vlad.com", house)
        issue = create_issue("No Water", "Where is the water", vlad, house)
        self.assertTrue(Issue.objects.get(pk=1).closed == False)
        self.client.force_login(bad_agency)
        response = self.client.get(reverse("issues:api-issue-close-chat", args=(issue,)))
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Issue.objects.get(pk=1).closed == False)

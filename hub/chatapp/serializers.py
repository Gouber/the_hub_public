from django.contrib.auth.validators import UnicodeUsernameValidator
from rest_framework import serializers
from django.utils import timezone
from chatapp.models import Conversation, Chat
from login_register_service_hub.models import CustomUser


# NOTE: THIS IS NEEDED AS WE NEED TO SKIP THE UNIQUE VALIDATORS
# FOR THE NESTED SERIALIZER `ConversationSerializer`
# DO NOT USE THIS (`UserChatSerializer`) ANYWHERE ELSE!
class UserChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('email',)
        extra_kwargs = {
            'email': {
                'validators': [UnicodeUsernameValidator()],
            }
        }


class ChatSerializer(serializers.ModelSerializer):
    student = UserChatSerializer(read_only=True)
    date_sent = serializers.DateTimeField(default=timezone.now())
    message = serializers.CharField(max_length=500)

    class Meta:
        model = Chat
        fields = ('date_sent', 'student', 'message')

    def create(self, validated_data):
        user = validated_data.pop("user")
        conversation = validated_data.pop("conversation")
        instance = self.Meta.model(**validated_data)
        instance.student = user
        instance.conversation = conversation
        instance.save()
        return instance


class ConversationSerializer(serializers.ModelSerializer):
    students = UserChatSerializer(many=True)
    start_date = serializers.DateTimeField(default=timezone.now())

    class Meta:
        model = Conversation
        fields = ('start_date', 'students', 'id')

    def create(self, validated_data):
        user = validated_data.pop("user")
        emails_captured = validated_data.pop("students")
        extracted_emails = []
        for extracted_email in emails_captured:
            extracted_emails.append(str(extracted_email['email']))
        students_fetched = CustomUser.objects.filter(email__in=extracted_emails)
        instance = self.Meta.model(**validated_data)
        instance.save()
        instance.students.add(user)
        for student in students_fetched:
            instance.students.add(student)
        instance.save()
        return instance


class ConversationWithChatSerializer(serializers.ModelSerializer):
    students = UserChatSerializer(many=True)
    start_date = serializers.DateTimeField()
    chat_set = ChatSerializer(many=True)

    class Meta:
        model = Conversation
        fields = ('start_date', 'students', 'chat_set', 'id')


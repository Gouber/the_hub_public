from rest_framework import serializers
from issues.models import Issue, Message


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ('title', 'pub_date', 'closed', 'id')


class MessageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('text', 'date_sent', 'sender')


class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ('text', 'date_sent',)

    def create(self, validated_data):
        user = validated_data.pop("user")
        issue = validated_data.pop("issue")
        return Message.objects.create(**validated_data, sender=user, issue=issue)


class IssueWithMessageSerializer(serializers.ModelSerializer):
    message = serializers.CharField(required=True)

    class Meta:
        model = Issue
        fields = ('title', 'message', 'hidden')

    def create(self, validated_data):
        user = validated_data.pop('user')
        message_associated = validated_data.pop('message')
        issue = Issue.objects.create(**validated_data)
        Message.objects.create(sender=user, issue=issue, date_sent=issue.pub_date, text=message_associated)
        return issue

from rest_framework import generics, status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import Http404
from chatapp.models import Conversation
from chatapp.serializers import ConversationSerializer, ChatSerializer, ConversationWithChatSerializer


# TODO - add proper permission for all of these

class CreateConversationAPIView(generics.CreateAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, ]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # TODO: A catalogue with the people that this person can actually create a chat with.
            serializer.save(user=self.request.user)
            return Response(status=status.HTTP_201_CREATED)
        else:
            raise ValueError(serializer.errors)


class CreateChatAPIView(generics.CreateAPIView):
    serializer_class = ChatSerializer
    # TODO - check conversation belongs to user requesting
    permission_classes = [IsAuthenticated, ]

    def create(self, request, *args, **kwargs):
        conversation = get_object_or_404(Conversation, pk=kwargs['pk'])

        if not Conversation.objects.filter(pk=kwargs['pk'], students=self.request.user):
            raise Http404

        serializer = self.serializer_class(data=request.data, )
        if serializer.is_valid():
            serializer.save(user=self.request.user, conversation=conversation)
            return Response(data=serializer.data,status=status.HTTP_201_CREATED)
        else:
            raise ValueError(serializer.errors)


class ListOfChatForConversation(generics.ListAPIView):
    serializer_class = ConversationWithChatSerializer
    permission_classes = [IsAuthenticated, ]

    # TODO - check conversation belongs to user requesting

    def get_queryset(self):
        return Conversation.objects.filter(students=self.request.user, pk=self.request.query_params.get('pk', None))


# TODO - Can we delete this?
class ListConversation(generics.ListAPIView):
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return Conversation.objects.filter(students=self.request.user)


# Notice this also inherits the permission to be authenticated
class ListConversationWithChat(ListConversation):
    serializer_class = ConversationWithChatSerializer

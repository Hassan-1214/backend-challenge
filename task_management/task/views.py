from rest_framework import viewsets, permissions
from .models import Task, Label
from .serializers import TaskSerializer, LabelSerializer
from rest_framework.authentication import SessionAuthentication


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Task.objects.filter(owner=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}


class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.all()
    serializer_class = LabelSerializer
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)

    def get_serializer_context(self):
        return {'request': self.request}

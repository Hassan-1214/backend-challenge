from rest_framework import serializers
from .models import Task, Label


class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['id', 'name', 'owner']
        read_only_fields = ['owner']

    def create(self, validated_data):
        user = self.context['request'].user
        task = Label.objects.create(owner=user, **validated_data)
        return task


class TaskSerializer(serializers.ModelSerializer):
    labels = LabelSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'is_completed', 'owner', 'labels']
        read_only_fields = ['owner']

    def create(self, validated_data):
        user = self.context['request'].user
        task = Task.objects.create(owner=user, **validated_data)
        return task

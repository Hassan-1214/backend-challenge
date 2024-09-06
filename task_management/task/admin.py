from django.contrib import admin
from .models import Task, Label


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_completed', 'owner']
    search_fields = ['title', 'owner__username']
    list_filter = ['is_completed', 'owner']


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner']
    search_fields = ['name', 'owner__username']
    list_filter = ['owner']

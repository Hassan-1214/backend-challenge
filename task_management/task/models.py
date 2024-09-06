from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Label(models.Model):
    name  = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(User, related_name='labels', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Task(models.Model):
    title = models.CharField(max_length=200, blank=False, null=False)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    owner = models.ForeignKey(User, related_name='tasks', on_delete=models.CASCADE)
    labels = models.ManyToManyField(Label, related_name='tasks', blank=True)

    def __str__(self):
        return self.title
    
    def clean(self):
        # Ensure title is not empty or whitespace
        if not self.title.strip():
            raise ValidationError('Title cannot be empty or whitespace.')
        
        # Ensure title does not exceed 200 characters
        if len(self.title) > 200:
            raise ValidationError('Title cannot exceed 200 characters.')

    def save(self, *args, **kwargs):
        # Run full_clean to trigger validation before saving
        self.full_clean()
        super(Task, self).save(*args, **kwargs)

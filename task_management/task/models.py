from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

User = settings.AUTH_USER_MODEL


class Label(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, related_name='labels', on_delete=models.CASCADE)

    class Meta:
        unique_together = ('name', 'owner')  # Ensures label names are unique per user

    def clean(self):
        if not self.name:
            raise ValidationError('Label name cannot be empty.')
        if len(self.name) > 255:
            raise ValidationError('Label name is too long.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    owner = models.ForeignKey(User, related_name='tasks', on_delete=models.CASCADE)
    labels = models.ManyToManyField(Label, related_name='tasks', blank=True)

    def clean(self):
        if not self.title.strip():
            raise ValidationError('Task title cannot be empty or just whitespace.')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

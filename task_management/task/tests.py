from django.test import TestCase
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from .models import Label, Task

class TaskLabelTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpass')
        # Create test labels and tasks
        self.label = Label.objects.create(name='Urgent', owner=self.user)
        self.task = Task.objects.create(title='Test Task', description='Test description', owner=self.user)

    def test_create_label_success(self):
        # Create a new label
        new_label = Label.objects.create(name='Important', owner=self.user)
        self.assertEqual(new_label.name, 'Important')
        self.assertEqual(new_label.owner, self.user)

    def test_create_label_fail(self):
        # Try creating a label with the same name (should fail due to unique constraint)
        with self.assertRaises(IntegrityError):
            Label.objects.create(name='Urgent', owner=self.user)
    
    def test_create_task_success(self):
        # Create a new task
        new_task = Task.objects.create(title='New Task', owner=self.user)
        self.assertEqual(new_task.title, 'New Task')
        self.assertEqual(new_task.owner, self.user)
    
    def test_create_task_fail(self):
        # Try creating a task without a title (should fail due to CharField constraints)
        with self.assertRaises(Exception):
            Task.objects.create(title='', owner=self.user)

    def test_update_task_success(self):
        # Update an existing task's title
        self.task.title = 'Updated Task'
        self.task.save()
        updated_task = Task.objects.get(id=self.task.id)
        self.assertEqual(updated_task.title, 'Updated Task')

    def test_update_task_fail(self):
        # Try updating task with a long title (should fail due to max_length constraint)
        with self.assertRaises(Exception):
            self.task.title = 'T' * 2010  # More than 200 chars
            self.task.save()
    
    def test_delete_label_success(self):
        # Delete an existing label
        self.label.delete()
        with self.assertRaises(Label.DoesNotExist):
            Label.objects.get(id=self.label.id)

    def test_delete_label_fail(self):
        # Try deleting a non-existing label (should fail)
        with self.assertRaises(Label.DoesNotExist):
            Label.objects.get(id=999)

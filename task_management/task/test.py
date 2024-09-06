import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from .models import Task, Label

User = get_user_model()


@pytest.mark.django_db
class TestTaskManagementViewSets:

    @pytest.fixture(autouse=True)
    def setup(self):
        # Create test users and client
        self.client = APIClient()
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')

        # Create tasks and labels for user1
        self.task1 = Task.objects.create(
            title="Task 1",
            description="Description 1",
            owner=self.user1
        )
        self.label1 = Label.objects.create(
            name="Label 1",
            owner=self.user1
        )

    @pytest.mark.parametrize(
        "task_data, expected_status, login_user, expected_title, description, expected_task_count",
        [
            (
                {"title": "New Task", "description": "New Task Description"},
                status.HTTP_201_CREATED,
                "user1",
                "New Task",
                "New Task Description",
                2
            ),  # Valid task
            (
                {"title": "", "description": "Empty Title Task"},
                status.HTTP_400_BAD_REQUEST,
                "user1",
                "",
                "Empty Title Task",
                1
            ),  # Missing title
            (
                {"title": "Invalid User Task", "description": "Task by Invalid User"},
                status.HTTP_403_FORBIDDEN,
                "user2",
                "Invalid User Task",
                "Task by Invalid User",
                1
            ),  # User2 creating task for User1
            (
                {"title": "Short Title", "description": ""},
                status.HTTP_201_CREATED,
                "user1",
                "Short Title",
                "",
                2
            ),  # Valid case with missing description
            (
                {"title": "Task with long description", "description": "a" * 1000},
                status.HTTP_201_CREATED,
                "user1",
                "Task with long description",
                "a" * 1000,
                2
            ),  # Very long description
        ]
    )
    def test_create_task_with_various_data(
        self, task_data, expected_status, login_user, expected_title, description, expected_task_count
    ):
        self.client.login(username=login_user, password='password1')
        response = self.client.post('/api/tasks/', task_data, format='json')
        assert response.status_code == expected_status
        if expected_status == status.HTTP_201_CREATED:
            assert Task.objects.filter(
                title=expected_title,
                description=description
            ).exists()
            assert Task.objects.count() == expected_task_count

    @pytest.mark.parametrize(
        "label_data, expected_status, login_user, expected_label_count, expected_label_name",
        [
            (
                {"name": "New Label"},
                status.HTTP_201_CREATED,
                "user1",
                2,
                "New Label"
            ),  # Valid label
            (
                {"name": ""},
                status.HTTP_400_BAD_REQUEST,
                "user1",
                1,
                ""
            ),  # Missing label name
            (
                {"name": "Label by user2"},
                status.HTTP_403_FORBIDDEN,
                "user2",
                1,
                "Label by user2"
            ),  # User2 trying to create label for User1
            (
                {"name": "a" * 256},
                status.HTTP_400_BAD_REQUEST,
                "user1",
                1,
                "a" * 256
            ),  # Label name too long
            (
                {"name": "Duplicate Label"},
                status.HTTP_201_CREATED,
                "user1",
                2,
                "Duplicate Label"
            ),  # Create a label with a duplicate name
        ]
    )
    def test_create_label_with_various_data(
        self, label_data, expected_status, login_user, expected_label_count, expected_label_name
    ):
        self.client.login(username=login_user, password='password1')
        response = self.client.post('/api/labels/', label_data, format='json')
        assert response.status_code == expected_status
        assert Label.objects.count() == expected_label_count

    @pytest.mark.parametrize(
        "user_login, task_id, expected_status, expected_task_owner, expected_access",
        [
            (
                {"username": "user1", "password": "password1"},
                1,
                status.HTTP_200_OK,
                "user1",
                True
            ),  # User1 should access their task
            (
                {"username": "user2", "password": "password2"},
                1,
                status.HTTP_404_NOT_FOUND,
                "user1",
                False
            ),  # User2 should not access User1's task
            (
                {"username": "user1", "password": "password1"},
                999,
                status.HTTP_404_NOT_FOUND,
                None,
                False
            ),  # Non-existent task
            (
                {"username": "user2", "password": "password2"},
                999,
                status.HTTP_404_NOT_FOUND,
                None,
                False
            ),  # Non-existent task for unauthorized user
            (
                {"username": "user1", "password": "password1"},
                1,
                status.HTTP_200_OK,
                "user1",
                True
            ),  # User1 checks their own task again
        ]
    )
    def test_task_access_restriction(
        self, user_login, task_id, expected_status, expected_task_owner, expected_access
    ):
        self.client.login(
            username=user_login['username'],
            password=user_login['password']
        )
        response = self.client.get(f'/api/tasks/{task_id}/')
        assert response.status_code == expected_status
        if expected_access:
            assert Task.objects.get(id=task_id).owner.username == expected_task_owner

    @pytest.mark.parametrize(
        "user_login, expected_task_count, expected_label_count",
        [
            (
                {"username": "user1", "password": "password1"},
                1,
                1
            ),  # User1 should have 1 task and 1 label
            (
                {"username": "user2", "password": "password2"},
                0,
                0
            ),  # User2 should have no tasks or labels
            (
                {"username": "user1", "password": "password1"},
                1,
                1
            ),  # User1 checks their task and label again
            (
                {"username": "user2", "password": "password2"},
                0,
                0
            ),  # User2 confirms they still have no tasks
            (
                {"username": "user1", "password": "password1"},
                1,
                1
            ),  # User1 confirms their task and label are intact
        ]
    )
    def test_get_tasks_and_labels_for_various_users(
        self, user_login, expected_task_count, expected_label_count
    ):
        self.client.login(
            username=user_login['username'],
            password=user_login['password']
        )

        # Check tasks
        task_response = self.client.get('/api/tasks/')
        assert task_response.status_code == status.HTTP_200_OK
        assert len(task_response.data) == expected_task_count

        # Check labels
        label_response = self.client.get('/api/labels/')
        assert label_response.status_code == status.HTTP_200_OK
        assert len(label_response.data) == expected_label_count

    @pytest.mark.parametrize(
        "login_user, label_id, expected_status, expected_owner_id",
        [
            (
                'user1',
                1,
                status.HTTP_200_OK,
                1
            ),  # User1 owns Label 1, should access it
            (
                'user2',
                1,
                status.HTTP_404_NOT_FOUND,
                None
            ),  # User2 cannot access Label 1 owned by User1
            (
                'user2',
                999,
                status.HTTP_404_NOT_FOUND,
                None
            ),  # Label with ID 999 doesn't exist
            (
                None,
                1,
                status.HTTP_403_FORBIDDEN,
                None
            ),  # Unauthorized access (no login)
            (
                'user1',
                1,
                status.HTTP_200_OK,
                1
            ),  # User1 access their own label
        ]
    )
    def test_get_label_access_scenarios(
        self, login_user, label_id, expected_status, expected_owner_id
    ):
        if login_user:
            self.client.login(
                username=login_user,
                password='password1' if login_user == 'user1' else 'password2'
            )
        response = self.client.get(f'/api/labels/{label_id}/')
        assert response.status_code == expected_status
        if expected_owner_id:
            assert response.data['owner'] == expected_owner_id


@pytest.mark.django_db
class TestLabelModel:

    @pytest.fixture(autouse=True)
    def setup(self):
        # Create test users
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')

    @pytest.mark.parametrize(
        "name, owner, expected_status",
        [
            ("Work", "user1", True),  # Valid label for user1
            ("Personal", "user1", True),  # Another valid label for user1
            ("Work", "user2", True),  # Same label name for user2, different owner
            ("", "user1", False),  # Empty label name
        ]
    )
    def test_label_creation(self, name, owner, expected_status):
        user = User.objects.get(username=owner)
        if expected_status:
            Label.objects.create(name=name, owner=user)
            assert Label.objects.filter(name=name, owner=user).exists()
        else:
            with pytest.raises(ValidationError):
                Label.objects.create(name=name, owner=user)

    @pytest.mark.parametrize(
        "name, owner, unique",
        [
            ("Work", "user1", True),  # First label with the name "Work"
            ("Work", "user1", False),  # Duplicate label for the same user
            ("Work", "user2", True),  # Same label name for a different user (valid)
        ]
    )
    def test_label_uniqueness(self, name, owner, unique):
        user = User.objects.get(username=owner)
        if unique:
            label = Label.objects.create(name=name, owner=user)
            assert label.pk is not None  # Check if label is created
        else:
            Label.objects.create(name=name, owner=user)
            with pytest.raises(ValidationError):
                Label.objects.create(name=name, owner=user)


@pytest.mark.django_db
class TestTaskModel:

    @pytest.fixture(autouse=True)
    def setup(self):
        # Create test users and labels
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password2')
        self.label1 = Label.objects.create(name="Work", owner=self.user1)
        self.label2 = Label.objects.create(name="Personal", owner=self.user1)

    @pytest.mark.parametrize(
        "title, description, is_completed, owner, labels, expected_status",
        [
            ("Task 1", "A valid task", False, "user1", ["Work"], True),  # Valid task with label
            ("Task 2", "", True, "user1", ["Work", "Personal"], True),  # Valid task with multiple labels
            ("", "Task with no title", False, "user1", ["Work"], False),  # Invalid task with empty title
            ("    ", "Task with whitespace title", False, "user1", [], False),  # Invalid task with whitespace title
            ("Task 3", "Task for another user", False, "user2", [], True),  # Task for a different user
        ]
    )
    def test_task_creation(
        self, title, description, is_completed, owner, labels, expected_status
    ):
        user = User.objects.get(username=owner)
        task_labels = Label.objects.filter(name__in=labels, owner=user)
        task = Task(
            title=title,
            description=description,
            is_completed=is_completed,
            owner=user
        )

        if expected_status:
            task.save()
            task.labels.add(*task_labels)
            assert Task.objects.filter(title=title, owner=user).exists()
        else:
            with pytest.raises(ValidationError):
                task.save()

    @pytest.mark.parametrize(
        "task_title, labels, expected_labels",
        [
            ("Task 1", ["Work"], 1),  # Task with 1 label
            ("Task 2", ["Work", "Personal"], 2),  # Task with 2 labels
            ("Task 3", [], 0),  # Task with no labels
        ]
    )
    def test_task_label_assignment(self, task_title, labels, expected_labels):
        task = Task.objects.create(title=task_title, owner=self.user1)
        task_labels = Label.objects.filter(name__in=labels, owner=self.user1)
        task.labels.add(*task_labels)
        assert task.labels.count() == expected_labels

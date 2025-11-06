from datetime import date, timedelta

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from users.models import CustomUser

from .models import Task


class TaskAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = CustomUser.objects.create_user(
            email="user1@test.com",
            password="Pass123!",
            first_name="User",
            last_name="One",
        )
        self.user2 = CustomUser.objects.create_user(
            email="user2@test.com",
            password="Pass123!",
            first_name="User",
            last_name="Two",
        )

    def test_unauthenticated_access_denied(self):
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_task_with_all_fields(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            "title": "Complete project",
            "description": "Finish the Django API",
            "status": "IN_PROGRESS",
            "priority": "HIGH",
            "due_date": str(date.today() + timedelta(days=7)),
        }
        response = self.client.post("/api/tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Complete project")
        self.assertEqual(response.data["priority"], "HIGH")

    def test_task_title_required(self):
        self.client.force_authenticate(user=self.user1)
        data = {"description": "No title provided"}
        response = self.client.post("/api/tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_only_see_own_tasks(self):
        self.client.force_authenticate(user=self.user1)
        Task.objects.create(title="User1 Task", user=self.user1)
        Task.objects.create(title="User2 Task", user=self.user2)

        response = self.client.get("/api/tasks/")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "User1 Task")

    def test_filter_by_status_and_priority(self):
        self.client.force_authenticate(user=self.user1)
        Task.objects.create(
            title="Task 1", status="TODO", priority="HIGH", user=self.user1
        )
        Task.objects.create(
            title="Task 2", status="DONE", priority="LOW", user=self.user1
        )
        Task.objects.create(
            title="Task 3", status="TODO", priority="LOW", user=self.user1
        )

        response = self.client.get("/api/tasks/?status=TODO&priority=HIGH")
        self.assertEqual(len(response.data["results"]), 1)

    def test_ordering_by_priority(self):
        self.client.force_authenticate(user=self.user1)
        Task.objects.create(title="Low Task", priority="LOW", user=self.user1)
        Task.objects.create(title="High Task", priority="HIGH", user=self.user1)

        response = self.client.get("/api/tasks/?ordering=-priority")
        self.assertEqual(response.data["results"][0]["title"], "High Task")

    def test_pagination_works(self):
        self.client.force_authenticate(user=self.user1)
        for i in range(25):
            Task.objects.create(title=f"Task {i}", user=self.user1)

        response = self.client.get("/api/tasks/")
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])

        response2 = self.client.get("/api/tasks/?page=2")
        self.assertEqual(len(response2.data["results"]), 10)


class TaskCRUDTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = CustomUser.objects.create_user(
            email="taskuser@test.com",
            password="TestPass123!",
            first_name="Task",
            last_name="User",
        )
        self.client.force_authenticate(user=self.user)

    def test_create_task(self):
        data = {"title": "Test Task", "description": "Test Description"}
        response = self.client.post("/api/tasks/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(Task.objects.first().user, self.user)

    def test_list_user_tasks(self):
        Task.objects.create(title="Task 1", user=self.user)
        Task.objects.create(title="Task 2", user=self.user)
        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_update_task(self):
        task = Task.objects.create(title="Original", user=self.user)
        data = {"title": "Updated", "description": "New desc"}
        response = self.client.put(f"/api/tasks/{task.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, "Updated")

    def test_delete_task(self):
        task = Task.objects.create(title="To Delete", user=self.user)
        response = self.client.delete(f"/api/tasks/{task.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_user_cannot_access_others_tasks(self):
        other_user = CustomUser.objects.create_user(
            email="other@test.com",
            password="Pass123!",
            first_name="Other",
            last_name="User",
        )
        task = Task.objects.create(title="Other Task", user=other_user)
        response = self.client.get(f"/api/tasks/{task.id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_task_pagination(self):
        for i in range(15):
            Task.objects.create(title=f"Task {i}", user=self.user)

        response = self.client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 10)
        self.assertIsNotNone(response.data["next"])

    def test_task_search(self):
        Task.objects.create(title="Meeting with client", user=self.user)
        Task.objects.create(title="Code review", user=self.user)

        response = self.client.get("/api/tasks/?search=meeting")
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]["title"], "Meeting with client")

    def test_task_filter_by_priority(self):
        Task.objects.create(title="High priority", priority="HIGH", user=self.user)
        Task.objects.create(title="Low priority", priority="LOW", user=self.user)

        response = self.client.get("/api/tasks/?priority=HIGH")
        self.assertEqual(len(response.data["results"]), 1)


from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Task

User = get_user_model()


class TaskAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )
        self.client.force_authenticate(user=self.user)

        self.task = Task.objects.create(
            title="Learn Django REST Framework",
            description="Write API tests",
            status=Task.Status.TODO,
            priority=2,
            created_by=self.user,
        )

    def test_list_tasks(self):
        response = self.client.get("/api/tasks/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(
            response.data["results"][0]["title"],
            "Learn Django REST Framework",
        )

    def test_create_task(self):
        payload = {
            "title": "Build API tests",
            "description": "Test task creation",
            "status": "todo",
            "priority": 3,
        }

        response = self.client.post(
            "/api/tasks/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(
            Task.objects.get(title="Build API tests").created_by,
            self.user,
        )

    def test_reject_blank_title(self):
        payload = {
            "title": "   ",
            "description": "Invalid task",
            "status": "todo",
            "priority": 1,
        }

        response = self.client.post(
            "/api/tasks/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(Task.objects.count(), 1)

    def test_filter_tasks_by_status(self):
        response = self.client.get(
            "/api/tasks/?status=todo"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_user_cannot_access_another_users_task(self):
        another_user = User.objects.create_user(
            username="anotheruser",
            password="AnotherPassword123!",
        )

        other_task = Task.objects.create(
            title="Private task",
            created_by=another_user,
        )

        response = self.client.get(
            f"/api/tasks/{other_task.pk}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


    def test_reject_priority_above_maximum(self):
        payload = {
            "title": "Invalid priority task",
            "priority": 4,
        }

        response = self.client.post(
            "/api/tasks/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("priority", response.data)


    def test_accept_maximum_priority(self):
        payload = {
            "title": "High priority task",
            "priority": 3,
        }

        response = self.client.post(
            "/api/tasks/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )


    def test_reject_invalid_status(self):
        payload = {
            "title": "Invalid status task",
            "status": "invalid",
            "priority": 1,
        }

        response = self.client.post(
            "/api/tasks/",
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("status", response.data)
        
        

    
    def test_reject_invalid_status_filter(self):
        response = self.client.get(
            "/api/tasks/?status=invalid"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("status", response.data)


    def test_reject_non_integer_priority_filter(self):
        response = self.client.get(
            "/api/tasks/?priority=high"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("priority", response.data)


    def test_reject_priority_filter_above_maximum(self):
        response = self.client.get(
            "/api/tasks/?priority=4"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertIn("priority", response.data)

    def test_reject_search_longer_than_200_characters(self):
        # Create a search string containing 201 characters.
        search_term = "a" * 201

        # Send the long string as a URL query parameter.
        response = self.client.get(
            "/api/tasks/",
            {"search": search_term},
        )

        # The serializer should reject the search string with HTTP 400.
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        # Confirm that the error identifies the search field.
        self.assertIn("search", response.data)


#Pagination Tests below:

    def test_pagination_returns_five_tasks_per_page(self):
        # setUp() already creates one task.
        # Create five more, giving us six tasks in total.
        for number in range(5):
            Task.objects.create(
                title=f"Extra task {number}",
                created_by=self.user,
            )

        response = self.client.get("/api/tasks/")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        # The default page size is five tasks.
        self.assertEqual(len(response.data["results"]), 5)

        # All six tasks should be counted, even though only five are returned.
        self.assertEqual(response.data["count"], 6)

        # A next-page link should exist because one task remains.
        self.assertIsNotNone(response.data["next"])

    def test_pagination_second_page(self):
        # Create six additional tasks.
        # Together with the task from setUp(), there are seven tasks.
        for number in range(6):
            Task.objects.create(
                title=f"Extra task {number}",
                created_by=self.user,
            )

        response = self.client.get("/api/tasks/?page=2")

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        # Seven tasks across pages of five means two tasks on page two.
        self.assertEqual(len(response.data["results"]), 2)

        # Page two is the final page, so there is no next page.
        self.assertIsNone(response.data["next"])

        # A previous-page link should be available.
        self.assertIsNotNone(response.data["previous"])

    def test_custom_page_size_is_limited(self):
        # Create 24 additional tasks, giving us 25 tasks total.
        for number in range(24):
            Task.objects.create(
                title=f"Extra task {number}",
                created_by=self.user,
            )

        # Request 100 tasks per page, exceeding max_page_size=20.
        response = self.client.get(
            "/api/tasks/?page_size=100"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        # DRF should enforce the maximum page size of 20.
        self.assertEqual(len(response.data["results"]), 20)
        self.assertEqual(response.data["count"], 25)


        """
        Understand the paginated response:
        ------
        
        A successful request returns JSON similar to this:
        ------


            json
            ----
            
            {
            "count": 6,
            "next": "http://testserver/api/tasks/?page=2",
            "previous": null,
            "results": [
                {
                "id": 1,
                "title": "Learn Django REST Framework",
                "description": "Write API tests",
                "status": "todo",
                "priority": 2,
                "due_date": null,
                "created_at": "...",
                "updated_at": "..."
                }
            ]
            }
            
        The example shows one result for illustration; a real first page can contain up to five results by default.

        count: Total number of matching tasks across all pages.

        next: URL for the next page, or null if no next page exists.

        previous: URL for the previous page, or null if there isn't one.

        results: The tasks on the current page.

        One important distinction: count reflects the tasks matching the user's filters, not just the tasks displayed on the current page.
        """
        
        
        
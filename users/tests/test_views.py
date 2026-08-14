from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User


class UserRegistrationTests(APITestCase):
    def test_register_user(self):
        url = reverse("users:register")

        data = {
            "email": "user@example.com",
            "first_name": "User",
            "last_name": "Example",
            "password": "testpassword123",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            User.objects.filter(email="user@example.com").exists()
        )

        user = User.objects.get(email="user@example.com")

        self.assertTrue(user.check_password("testpassword123"))
        self.assertEqual(user.first_name, "User")
        self.assertEqual(user.last_name, "Example")

    def test_register_user_without_email(self):
        url = reverse("users:register")

        data = {
            "first_name": "User",
            "last_name": "Example",
            "password": "testpassword123",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_with_existing_email(self):
        User.objects.create_user(
            email="user@example.com",
            password="testpassword123",
        )

        url = reverse("users:register")

        data = {
            "email": "user@example.com",
            "first_name": "User",
            "last_name": "Example",
            "password": "testpassword123",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JWTTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="testpassword123",
        )

    def test_obtain_token(self):
        url = reverse("users:token")

        data = {
            "email": "user@example.com",
            "password": "testpassword123",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_obtain_token_with_wrong_password(self):
        url = reverse("users:token")

        data = {
            "email": "user@example.com",
            "password": "wrongpassword",
        }

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserMeTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="user@example.com",
            password="testpassword123",
            first_name="User",
            last_name="Example",
        )

        self.client.force_authenticate(user=self.user)

    def test_get_my_profile(self):
        url = reverse("users:me")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "user@example.com")
        self.assertEqual(response.data["first_name"], "User")
        self.assertEqual(response.data["last_name"], "Example")

    def test_update_my_profile(self):
        url = reverse("users:me")

        data = {
            "first_name": "NewUser",
            "last_name": "NewExample",
        }

        response = self.client.patch(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, "NewUser")
        self.assertEqual(self.user.last_name, "NewExample")

    def test_unauthenticated_user_cannot_access_profile(self):
        self.client.force_authenticate(user=None)

        url = reverse("users:me")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_cannot_change_is_staff(self):
        url = reverse("users:me")

        response = self.client.patch(
            url,
            {"is_staff": True},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()

        self.assertFalse(self.user.is_staff)

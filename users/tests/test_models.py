from django.test import TestCase

from users.models import User


class UserModelTests(TestCase):
    def test_create_user_with_email(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="testpassword123",
            first_name="test",
            last_name="example",
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.first_name, "test")
        self.assertEqual(user.last_name, "example")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.check_password("testpassword123"))

    def test_create_user_without_email(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="",
                password="testpassword123",
            )

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpassword123",
        )

        self.assertEqual(user.email, "admin@example.com")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password("adminpassword123"))

    def test_email_is_unique(self):
        User.objects.create_user(
            email="test@example.com",
            password="testpassword123",
        )

        with self.assertRaises(Exception):
            User.objects.create_user(
                email="test@example.com",
                password="anotherpassword123",
            )

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


class TestUserModel(TestCase):
    """
    Test for Custom User model
    """
    def test_creating_user_with_valid_email(self):
        """
        Creating a user with valid email
        should match the assigned email with the saved email
        """
        email = 'test@example.com'
        password = 'testpass1234'
        username = 'myusername'
        first_name = 'firstname'
        last_name = 'lastname'

        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_creating_user_without_email(self):
        """
        Creating a user without email
        should raise ValueError
        """
        email = ''
        password = 'testpass1234'
        username = 'myusername'
        first_name = 'firstname'
        last_name = 'lastname'

        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(
                email=email,
                password=password,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )

    def test_creating_user_without_username(self):
        """
        Creating a user without username
        should raise ValueError
        """
        email = 'test@example.com'
        password = 'testpass1234'
        username = ''
        first_name = 'firstname'
        last_name = 'lastname'

        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(
                email=email,
                password=password,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )

    def test_creating_user_without_first_name(self):
        """
        Creating a user without first name
        should raise ValueError
        """
        email = 'test@example.com'
        password = 'testpass1234'
        username = 'myusername'
        first_name = ''
        last_name = 'lastname'

        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(
                email=email,
                password=password,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )

    def test_creating_user_with_short_first_name(self):
        """
        Creating a user with short first name
        should raise ValueError
        """
        email = 'test@example.com'
        password = 'testpass1234'
        username = 'myusername'
        first_name = 'a'
        last_name = 'lastname'

        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(
                email=email,
                password=password,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )

    def test_creating_user_without_last_name(self):
        """
        Creating a user without last name
        should raise ValueError
        """
        email = 'test@example.com'
        password = 'testpass1234'
        username = 'myusername'
        first_name = 'firstname'
        last_name = ''

        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(
                email=email,
                password=password,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )

    def test_creating_user_with_short_last_name(self):
        """
        Creating a user with short last name
        should raise ValueError
        """
        email = 'test@example.com'
        password = 'testpass1234'
        username = 'myusername'
        first_name = 'firstname'
        last_name = 'a'

        with self.assertRaises(ValidationError):
            get_user_model().objects.create_user(
                email=email,
                password=password,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )

    def test_creating_superuser(self):
        """
        Creating a superuser
        should have attributes is_superuser and is_staff
        and must be equal to True
        """
        email = 'admin@example.com'
        password = 'admin1234'
        username = 'admin'
        first_name = 'firstname'
        last_name = 'lastname'

        admin = get_user_model().objects.create_superuser(
            email=email,
            password=password,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )

        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)

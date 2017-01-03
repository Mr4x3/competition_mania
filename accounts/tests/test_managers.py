# inbuilt python imports
import unittest

# inbuilt django imports
from django.test import Client
from django.db.utils import IntegrityError
from django.conf import settings

# third-party django imports

# inter-app imports
import pytest

# local imports
from ..models import User



@pytest.mark.django_db
class TestUserManagerCreateUser(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user_data = {
            'email': 'test@test.com',
            'password': settings.TEST_USER_PASSWORD,
            'first_name': 'Jon',
            'last_name': 'Snow'
        }

    def test_user_created_using_create_user(self):
        User.objects.create_user(**self.user_data)
        self.assertEqual(User.objects.count(), 1)

    def test_user_not_created_if_email_not_provided(self):
        del self.user_data['email']
        self.assertRaises(TypeError, User.objects.create_user, **self.user_data)

    def test_user_not_created_if_first_name_not_provided(self):
        del self.user_data['first_name']
        self.assertRaises(TypeError, User.objects.create_user, **self.user_data)

    def test_user_not_created_if_last_name_not_provided(self):
        del self.user_data['last_name']
        self.assertRaises(TypeError, User.objects.create_user, **self.user_data)

    def test_correct_first_name(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.first_name, 'Jon')

    def test_correct_last_name(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.last_name, 'Snow')

    def test_correct_email(self):
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, 'test@test.com')

    def test_password_stored_in_hashed_format(self):
        user = User.objects.create_user(**self.user_data)
        self.assertNotEqual(user.password, settings.TEST_USER_PASSWORD)
        self.assertTrue(user.check_password(settings.TEST_USER_PASSWORD))

    def test_superuser_not_created_by_default(self):
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

    def test_cannot_create_user_with_same_email(self):
        User.objects.create_user(**self.user_data)
        self.assertEqual(User.objects.filter(email=self.user_data['email']).count(), 1)
        self.assertRaises(IntegrityError, User.objects.create_user, **self.user_data)


@pytest.mark.django_db
class TestUserManagerCreateSuperuser(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user_data = {
            'email': 'test@test.com',
            'password': settings.TEST_USER_PASSWORD,
            'first_name': 'Jon',
            'last_name': 'Snow'
        }

    def test_superuser_created_using_create_superuser(self):
        User.objects.create_superuser(**self.user_data)
        self.assertEqual(User.objects.count(), 1)

    def test_superuser_not_created_if_email_not_provided(self):
        del self.user_data['email']
        self.assertRaises(TypeError, User.objects.create_superuser, **self.user_data)

    def test_superuser_not_created_if_first_name_not_provided(self):
        del self.user_data['first_name']
        self.assertRaises(TypeError, User.objects.create_superuser, **self.user_data)

    def test_superuser_not_created_if_last_name_not_provided(self):
        del self.user_data['last_name']
        self.assertRaises(TypeError, User.objects.create_superuser, **self.user_data)

    def test_superuser_properties_set(self):
        user = User.objects.create_superuser(**self.user_data)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_cannot_create_superuser_with_same_email(self):
        User.objects.create_superuser(**self.user_data)
        self.assertEqual(User.objects.filter(email=self.user_data['email']).count(), 1)
        self.assertRaises(IntegrityError, User.objects.create_superuser, **self.user_data)

    def test_correct_first_name(self):
        user = User.objects.create_superuser(**self.user_data)
        self.assertEqual(user.first_name, 'Jon')

    def test_correct_last_name(self):
        user = User.objects.create_superuser(**self.user_data)
        self.assertEqual(user.last_name, 'Snow')

    def test_correct_email(self):
        user = User.objects.create_superuser(**self.user_data)
        self.assertEqual(user.email, 'test@test.com')

    def test_password_stored_in_hashed_format(self):
        user = User.objects.create_superuser(**self.user_data)
        self.assertNotEqual(user.password, settings.TEST_USER_PASSWORD)
        self.assertTrue(user.check_password(settings.TEST_USER_PASSWORD))

# inbuilt python imports
import unittest

# inbuilt django imports
from django.test import Client
from django.conf import settings

# third-party django imports
import pytest

# inter-app imports
from sportsvitae.shared.factories import UserFactory

# local imports
from ..backends import EmailAuthenticationBackend, MobileAuthenticationBackend


@pytest.mark.django_db
class TestEmailAuthenticationBackend(unittest.TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.email_backend = EmailAuthenticationBackend()

    def test_returns_user_if_valid_credentials(self):
        user = self.email_backend.authenticate(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_returns_none_if_invalid_credentials(self):
        user = self.email_backend.authenticate(username='a@a.com', password='aaaaaa')
        self.assertIsNone(user)

    def test_returns_none_if_valid_email_but_invalid_password(self):
        user = self.email_backend.authenticate(username=self.user.email, password='aaaaaa')
        self.assertIsNone(user)

    def test_returns_user_with_pk(self):
        user = self.email_backend.get_user(self.user.id)
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_does_not_return_user_with_invalid_pk(self):
        user = self.email_backend.get_user(999)
        self.assertIsNone(user)


@pytest.mark.django_db
class TestMobileAuthenticationBackend(unittest.TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.mobile_backend = MobileAuthenticationBackend()

    def test_returns_user_if_valid_credentials(self):
        user = self.mobile_backend.authenticate(username=self.user.mobile, password=settings.TEST_USER_PASSWORD)
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_returns_none_if_invalid_credentials(self):
        user = self.mobile_backend.authenticate(username='9191919191', password='aaaaaa')
        self.assertIsNone(user)

    def test_returns_none_if_valid_email_but_invalid_password(self):
        user = self.mobile_backend.authenticate(username=self.user.mobile, password='aaaaaa')
        self.assertIsNone(user)

    def test_returns_user_with_pk(self):
        user = self.mobile_backend.get_user(self.user.id)
        self.assertIsNotNone(user)
        self.assertEqual(user, self.user)

    def test_does_not_return_user_with_invalid_pk(self):
        user = self.mobile_backend.get_user(999)
        self.assertIsNone(user)

# inbuilt python imports
import unittest
from datetime import datetime
import base64

# inbuilt django imports

# third-party django imports
import pytest
import fudge
from django.conf import settings
from Crypto.Cipher import XOR

# inter-app imports
from sportsvitae.shared.factories import UserFactory

# local imports
from ..utils import get_first_and_last_name, encode_token, decode_token, is_token_valid
from ..models import User


class TestFullNameSplitter(unittest.TestCase):

    def setUp(self):
        self.name = 'jon snow'

    def test_returns_correct_first_last_name(self):
        first_name, last_name = get_first_and_last_name(self.name)
        self.assertEqual(first_name, 'jon')
        self.assertEqual(last_name, 'snow')

    def test_returns_correct_first_last_name_with_spaces_removed(self):
        self.name = '  jon snow  '
        first_name, last_name = get_first_and_last_name(self.name)
        self.assertEqual(first_name, 'jon')
        self.assertEqual(last_name, 'snow')

    def test_returns_correct_with_dot_and_space(self):
        self.name = 'jon. snow'
        first_name, last_name = get_first_and_last_name(self.name)
        self.assertEqual(first_name, 'jon.')
        self.assertEqual(last_name, 'snow')

    def test_returns_correct_with_dot(self):
        self.name = 'jon.snow'
        first_name, last_name = get_first_and_last_name(self.name)
        self.assertEqual(first_name, 'jon')
        self.assertEqual(last_name, 'snow')

    def test_returns_correct_with_multiple_words(self):
        self.name = 'jon snow stark'
        first_name, last_name = get_first_and_last_name(self.name)
        self.assertEqual(first_name, 'jon snow')
        self.assertEqual(last_name, 'stark')

    def test_returns_correct_with_multiple_words_and_dot(self):
        self.name = 'jon snow. stark'
        first_name, last_name = get_first_and_last_name(self.name)
        self.assertEqual(first_name, 'jon snow.')
        self.assertEqual(last_name, 'stark')

    def test_returns_no_last_name_if_one_word(self):
        self.name = 'jon'
        first_name, last_name = get_first_and_last_name(self.name)
        self.assertEqual(first_name, 'jon')
        self.assertEqual(last_name, '')

    def test_returns_no_last_name_if_one_word(self):
        self.name = 'jon'
        first_name, last_name = get_first_and_last_name(self.name)
        self.assertEqual(first_name, 'jon')
        self.assertEqual(last_name, '')

    def test_returns_no_last_name_if_one_word_with_dot(self):
        self.name = 'jon.'
        first_name, last_name = get_first_and_last_name(self.name)
        self.assertEqual(first_name, 'jon.')
        self.assertEqual(last_name, '')


class TestEncodeToken(unittest.TestCase):

    def setUp(self):
        self.email = 'test@test.com'
        self.token_type = 1

    def test_returns_token(self):
        self.assertTrue(encode_token(email=self.email, token_type=self.token_type))

    def test_returns_token_as_string(self):
        token = encode_token(email=self.email, token_type=self.token_type)
        self.assertTrue(isinstance(token, str))


@pytest.mark.django_db
class TestDecodeToken(unittest.TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.email = self.user.email
        self.token_type = 1
        self.token = encode_token(email=self.email, token_type=self.token_type)

    def test_decodes_token(self):
        user, token_type, token_expired = decode_token(self.token)
        self.assertTrue(user)
        self.assertTrue(token_type)
        self.assertFalse(token_expired)

    def test_returns_user(self):
        user, token_type, token_expired = decode_token(self.token)
        self.assertTrue(user)
        self.assertEqual(user, self.user)

    def test_returns_token_type(self):
        user, token_type, token_expired = decode_token(self.token)
        self.assertTrue(token_type)
        self.assertEqual(token_type, self.token_type)

    def test_returns_token_expired_flag(self):
        user, token_type, token_expired = decode_token(self.token)
        self.assertFalse(token_expired)

    def test_returns_error_for_token_in_bytestring(self):
        token_bytestring = bytes(self.token, 'utf-8')
        self.assertRaises(TypeError, decode_token, token_bytestring)

    def test_does_not_return_user_for_token_from_non_existent_email(self):
        self.email = 'a@a.com'
        token = encode_token(email=self.email, token_type=self.token_type)
        user, token_type, token_expired = decode_token(token)
        self.assertIsNone(user)

    def test_does_not_return_token_type_for_token_from_non_existent_email(self):
        self.email = 'a@a.com'
        token = encode_token(email=self.email, token_type=self.token_type)
        user, token_type, token_expired = decode_token(token)
        self.assertIsNone(token_type)

    def test_returns_token_expired_for_token_from_non_existent_email(self):
        self.email = 'a@a.com'
        token = encode_token(email=self.email, token_type=self.token_type)
        user, token_type, token_expired = decode_token(token)
        self.assertTrue(token_expired)

    def test_does_not_return_user_for_token_from_invalid_email(self):
        self.email = 'invalid_email'
        token = encode_token(email=self.email, token_type=self.token_type)
        user, token_type, token_expired = decode_token(token)
        self.assertIsNone(user)

    def test_does_not_return_token_type_for_token_from_invalid_email(self):
        self.email = 'invalid_email'
        token = encode_token(email=self.email, token_type=self.token_type)
        user, token_type, token_expired = decode_token(token)
        self.assertIsNone(token_type)

    def test_returns_token_expired_for_token_from_invalid_email(self):
        self.email = 'invalid_email'
        token = encode_token(email=self.email, token_type=self.token_type)
        user, token_type, token_expired = decode_token(token)
        self.assertTrue(token_expired)


@pytest.mark.django_db
class TestIsTokenValid(unittest.TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.email = self.user.email
        self.token_type = 1

        self.token_expiry_date = datetime(2011, 1, 1, 0, 0)
        self.input_string = '{salt}|{email}|{token_type}|{token_expiry_date}'.format(salt=settings.TOKEN_ENCODE_SALT, email=self.email, token_type=0, token_expiry_date=self.token_expiry_date)
        self.xor_cipher = XOR.new(key=settings.TOKEN_ENCODE_SALT)
        self.expired_token = self.xor_cipher.encrypt(plaintext=bytes(self.input_string, 'utf-8') )
        self.expired_token = base64.urlsafe_b64encode(self.expired_token).decode('utf-8')

    def test_returns_valid_token(self):
        token = encode_token(email=self.email, token_type=self.token_type)
        self.assertTrue(is_token_valid(token))

    def test_returns_false_if_no_user_exists(self):
        User.objects.all().delete()
        token = encode_token(email=self.email, token_type=self.token_type)
        self.assertFalse(is_token_valid(token))

    def test_returns_false_if_token_expired(self):
        self.assertFalse(is_token_valid(self.expired_token))

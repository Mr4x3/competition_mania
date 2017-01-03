# inbuilt python imports
import unittest
import shutil
import os
from datetime import datetime

# inbuilt django imports
from django.test import Client
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

# third-party django imports
import pytest

# inter-app imports
from sportsvitae.shared.factories import UserFactory, MidoutUserFactory, CricketerFactory

# local imports
from ..forms import LoginForm, UserRegistrationForm, ProfileSpecificRegistrationForm, ChangePasswordForm, EditUserProfileForm
from ..models import User


@pytest.mark.django_db
class TestLoginForm(unittest.TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.form_data = {
            'email' : self.user.email,
            'password': settings.TEST_USER_PASSWORD
        }
        self.form_data_with_prefix = {
            'login-email' : self.user.email,
            'login-password': settings.TEST_USER_PASSWORD
        }
        self.login_form = LoginForm(self.form_data)
        self.login_form_with_prefix = LoginForm(self.form_data_with_prefix, prefix='login')

    def test_instantiation(self):
        self.assertTrue(self.login_form)

    def test_instantiation_with_prefix(self):
        self.assertTrue(self.login_form_with_prefix)

    def test_login_form_valid(self):
        self.assertTrue(self.login_form.is_valid())

    def test_form_is_not_multipart(self):
        login_form = LoginForm()
        self.assertFalse(login_form.is_multipart())

    def test_login_form_with_prefix_valid(self):
        self.assertTrue(self.login_form_with_prefix.is_valid())

    def test_valid_form_returns_authenticated_user(self):
        self.assertTrue(self.login_form.is_valid())
        self.assertIsNotNone(self.login_form.get_authenticated_user())
        self.assertEqual(self.login_form.get_authenticated_user().id, self.user.id)

    def test_valid_form_with_prefix_returns_authenticated_user(self):
        self.assertTrue(self.login_form_with_prefix.is_valid())
        self.assertIsNotNone(self.login_form_with_prefix.get_authenticated_user())
        self.assertEqual(self.login_form_with_prefix.get_authenticated_user().id, self.user.id)

    def test_form_invalid_if_email_missing(self):
        del self.form_data['email']
        login_form = LoginForm(self.form_data)
        self.assertFalse(login_form.is_valid())
        self.assertIn('email', login_form.errors)
        self.assertIn('This field is required.', login_form.errors['email'])

    def test_form_invalid_if_password_missing(self):
        del self.form_data['password']
        login_form = LoginForm(self.form_data)
        self.assertFalse(login_form.is_valid())
        self.assertIn('password', login_form.errors)
        self.assertIn('This field is required.', login_form.errors['password'])

    def test_form_invalid_for_non_registered_user(self):
        self.form_data['email'] = 'a@a.com'
        login_form = LoginForm(self.form_data)
        self.assertFalse(login_form.is_valid())
        self.assertIn('email', login_form.errors)
        self.assertIn('This email is not registered with us.', login_form.errors['email'])

    def test_form_invalid_for_wrong_password(self):
        self.form_data['password'] = 'password'
        login_form = LoginForm(self.form_data)
        self.assertFalse(login_form.is_valid())
        self.assertIn('email', login_form.errors)
        self.assertIn('Email Id and Password do not match', login_form.errors['email'])

    def test_form_returns_user_none_if_not_valid(self):
        self.form_data['password'] = 'password'
        login_form = LoginForm(self.form_data)
        self.assertFalse(login_form.is_valid())
        self.assertIsNone(login_form.get_authenticated_user())

    def test_returns_error_if_wrong_email(self):
        self.form_data['email'] = 'invalid_email'
        login_form = LoginForm(self.form_data)
        self.assertFalse(login_form.is_valid())
        self.assertIn('email', login_form.errors)
        self.assertIn('Enter a valid email address.', login_form.errors['email'])

    def test_form_invalid_if_email_greater_than_255_characters(self):
        email = 'a'*250 + '@test.com'
        self.form_data['email'] = email
        login_form = LoginForm(self.form_data)
        self.assertFalse(login_form.is_valid())
        self.assertIn('email', login_form.errors)
        self.assertIn('Ensure this value has at most 255 characters (it has {}).'.format(len(email)), login_form.errors['email'])


@pytest.mark.django_db
class TestUserRegistrationForm(unittest.TestCase):

    def setUp(self):
        self.form_data = {
            'email': 'dummy@test.com',
            'password1': settings.TEST_USER_PASSWORD,
            'password2': settings.TEST_USER_PASSWORD,
            'name': 'Jon Snow',
            'gender': 'M'
        }
        self.registration_form = UserRegistrationForm(self.form_data)

    def test_instantiation(self):
        self.assertTrue(self.registration_form)

    def test_form_valid(self):
        self.assertTrue(self.registration_form.is_valid())

    def test_form_is_not_multipart(self):
        registration_form = UserRegistrationForm()
        self.assertFalse(registration_form.is_multipart())

    def test_user_saved(self):
        self.registration_form.save()
        self.assertEqual(User.objects.count(), 1)

    def test_user_saved_correctly(self):
        self.registration_form.is_valid()
        user = self.registration_form.save()
        self.assertEqual(user.email, self.form_data['email'])
        self.assertEqual(user.first_name, 'Jon')
        self.assertEqual(user.last_name, 'Snow')
        self.assertEqual(user.gender, self.form_data['gender'])

    def test_password_stored_in_hashed_format(self):
        user = self.registration_form.save()
        self.assertNotEqual(user.password, self.form_data['password1'])
        user.check_password(self.form_data['password1'])

    def test_form_invalid_if_email_missing(self):
        del self.form_data['email']
        registration_form = UserRegistrationForm(self.form_data)
        self.assertFalse(registration_form.is_valid())
        self.assertIn('email', registration_form.errors)
        self.assertIn('This field is required.', registration_form.errors['email'])

    def test_form_invalid_if_password1_missing(self):
        del self.form_data['password1']
        registration_form = UserRegistrationForm(self.form_data)
        self.assertFalse(registration_form.is_valid())
        self.assertIn('password1', registration_form.errors)
        self.assertIn('This field is required.', registration_form.errors['password1'])

    def test_form_invalid_if_password2_missing(self):
        del self.form_data['password2']
        registration_form = UserRegistrationForm(self.form_data)
        self.assertFalse(registration_form.is_valid())
        self.assertIn('password2', registration_form.errors)
        self.assertIn('This field is required.', registration_form.errors['password2'])

    def test_form_invalid_if_name_missing(self):
        del self.form_data['name']
        registration_form = UserRegistrationForm(self.form_data)
        self.assertFalse(registration_form.is_valid())
        self.assertIn('name', registration_form.errors)
        self.assertIn('This field is required.', registration_form.errors['name'])

    def test_form_invalid_if_gender_missing(self):
        del self.form_data['gender']
        registration_form = UserRegistrationForm(self.form_data)
        self.assertFalse(registration_form.is_valid())
        self.assertIn('gender', registration_form.errors)
        self.assertIn('This field is required.', registration_form.errors['gender'])

    def test_form_invalid_if_passwords_do_not_match(self):
        self.form_data['password2'] = 'dummy'
        registration_form = UserRegistrationForm(self.form_data)
        self.assertFalse(registration_form.is_valid())
        self.assertIn('password1', registration_form.errors)

    def test_form_invalid_if_password_less_than_6_characters(self):
        self.form_data['password1'] = 'abc'
        registration_form = UserRegistrationForm(self.form_data)
        self.assertFalse(registration_form.is_valid())
        self.assertIn('password1', registration_form.errors)

    def test_email_saved_in_lowercase(self):
        original_email = self.form_data['email'].upper()
        saved_email = original_email.lower()
        self.form_data['email'] = original_email
        self.registration_form.is_valid()
        user = self.registration_form.save()
        self.assertEqual(user.email, saved_email)

    def test_cannot_create_user_with_same_email(self):
        self.registration_form.is_valid()
        self.registration_form.save()
        self.assertTrue(User.objects.filter(email=self.form_data['email']).exists())
        registration_form2 = UserRegistrationForm(self.form_data)
        self.assertFalse(registration_form2.is_valid())
        self.assertIn('email', registration_form2.errors)

    def test_returns_error_if_wrong_name(self):
        self.form_data['name'] = 'jon.'
        registration_form = UserRegistrationForm(self.form_data)
        self.assertFalse(registration_form.is_valid())
        self.assertIn('name', registration_form.errors)
        self.assertIn('Please enter full name.', registration_form.errors['name'])

    def test_form_valid_if_name_with_dot(self):
        self.form_data['name'] = 'jon.snow'
        registration_form = UserRegistrationForm(self.form_data)
        self.assertTrue(registration_form.is_valid())

    def test_saves_name_correctly_with_dot(self):
        self.form_data['name'] = 'jon.snow'
        registration_form = UserRegistrationForm(self.form_data)
        self.assertTrue(registration_form.is_valid())
        user = registration_form.save()
        self.assertEqual(user.first_name, 'jon')
        self.assertEqual(user.last_name, 'snow')


@pytest.mark.django_db
class TestProfileSpecificRegistrationForm(unittest.TestCase):

    def setUp(self):
        self.user = MidoutUserFactory()
        self.form_data = {
            'email' : self.user.email,
            'name': 'Jon Snow',
            'gender' : 'M',
            'date_of_birth':'12/15/2015',
            'country': 'IN',
            'state': '1013',
            'state_text': '',
            'city': '10178',
            'city_text': '',
            'mobile': '9999999999',
        }

        self.form_data_international = {
            'email' : self.user.email,
            'name': 'Jon Snow',
            'gender' : 'M',
            'date_of_birth':'12/15/2015',
            'country': 'US',
            'state': '',
            'state_text': 'Ohio',
            'city': '',
            'city_text': 'xyz',
            'mobile': '9999999999',
        }

        self.display_picture_path = 'accounts/tests/test_display_pic.png'
        self.cover_picture_path = 'accounts/tests/test_cover_pic.png'

        self.file_data = {
            'display_picture':SimpleUploadedFile(name='test_display_pic.png', content=open(self.display_picture_path, 'rb').read()),
            'cover_picture': SimpleUploadedFile(name='test_cover_pic.png', content=open(self.cover_picture_path, 'rb').read())
        }
        self.profile_form = ProfileSpecificRegistrationForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.profile_form_international = ProfileSpecificRegistrationForm(data=self.form_data_international, files=self.file_data, instance=self.user)

    def tearDown(self):
        """
        Delete the test uploads
        """
        shutil.rmtree(settings.IMAGE_UPLOAD_DIR, ignore_errors=True)

    def test_instantiation(self):
        self.assertTrue(self.profile_form)
        self.assertTrue(self.profile_form_international)

    def test_form_valid(self):
        self.assertTrue(self.profile_form.is_valid())
        self.assertTrue(self.profile_form_international.is_valid())

    def test_form_is_multipart(self):
        profile_form = ProfileSpecificRegistrationForm()
        self.assertTrue(profile_form.is_multipart())

    def test_email_cannot_be_edited(self):
        self.form_data['email'] = 'test@testing.com'
        profile_form = ProfileSpecificRegistrationForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('email', profile_form.errors)
        self.assertIn('Email cannot be edited', profile_form.errors['email'])

    def test_email_field_readonly(self):
        profile_form = ProfileSpecificRegistrationForm()
        self.assertTrue(profile_form.fields['email'].widget.attrs['readonly'])

    def test_name_can_be_edited(self):
        self.form_data['name'] = 'some name'
        profile_form = ProfileSpecificRegistrationForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertTrue(profile_form.is_valid())
        user = profile_form.save()
        self.assertEqual(user.name, self.form_data['name'])

    def test_name_must_be_full(self):
        self.form_data['name'] = 'Jon'
        profile_form = ProfileSpecificRegistrationForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('name', profile_form.errors)
        self.assertIn('Please enter full name.', profile_form.errors['name'])

    def test_gender_can_be_edited(self):
        self.form_data['gender'] = 'F'
        self.assertNotEqual(self.user.gender, self.form_data['gender'])
        profile_form = ProfileSpecificRegistrationForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertTrue(profile_form.is_valid())
        user = profile_form.save()
        self.assertEqual(self.user.gender, self.form_data['gender'])

    def test_display_pic_can_be_empty(self):
        self.file_data['display_picture'] = ''
        profile_form = ProfileSpecificRegistrationForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertTrue(profile_form.is_valid())

    def test_cover_pic_can_be_empty(self):
        self.file_data['cover_picture'] = ''
        profile_form = ProfileSpecificRegistrationForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertTrue(profile_form.is_valid())

    def test_image_file_must_be_opened_in_rb_mode(self):
        with self.assertRaises(UnicodeDecodeError):
            SimpleUploadedFile(name='test_display_pic.png', content=open(self.display_picture_path).read())

    def test_image_file_content_must_be_read(self):
        with self.assertRaises(TypeError):
            SimpleUploadedFile(name='test_display_pic.png', content=open(self.display_picture_path, 'rb'))

    def test_content_does_not_accepts_string_content_in_mock_image_file(self):
        with self.assertRaises(TypeError):
            SimpleUploadedFile(name='test_display_pic.png', content='some_content')

    def test_not_accepts_invalid_non_image_display_pic_file(self):
        self.file_data['display_picture'] = SimpleUploadedFile(name='test_views.py', content=open('accounts/tests/test_views.py', 'rb').read())
        profile_form = ProfileSpecificRegistrationForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('display_picture', profile_form.errors)

    def test_not_accepts_invalid_non_image_cover_pic_file(self):
        self.file_data['cover_picture'] = SimpleUploadedFile(name='test_views.py', content=open('accounts/tests/test_views.py', 'rb').read())
        profile_form = ProfileSpecificRegistrationForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('cover_picture', profile_form.errors)

    def test_date_of_birth_saved_correctly(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        self.assertEqual(user.date_of_birth.year, 2015)
        self.assertEqual(user.date_of_birth.month, 12)
        self.assertEqual(user.date_of_birth.day, 15)

    def test_gender_saved_correctly(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        self.assertEqual(user.gender, 'M')

    def test_country_saved_correctly(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        self.assertEqual(user.country, 'IN')

    def test_state_saved_correctly(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        self.assertEqual(user.state, 1013)
        self.assertEqual(user.state_text, '')

    def test_city_saved_correctly(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        self.assertEqual(user.city, 10178)
        self.assertEqual(user.city_text, '')

    def test_returns_error_if_no_state_for_india(self):
        self.form_data['state'] = ''
        profile_form = ProfileSpecificRegistrationForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('state', profile_form.errors)
        self.assertIn("Please choose a value for state", profile_form.errors['state'])

    def test_returns_error_if_no_city_for_india(self):
        self.form_data['city'] = ''
        profile_form = ProfileSpecificRegistrationForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('city', profile_form.errors)
        self.assertIn("Please choose a value for city", profile_form.errors['city'])

    def test_returns_error_if_city_of_different_state(self):
        self.form_data['city'] = 10050
        profile_form = ProfileSpecificRegistrationForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('city', profile_form.errors)
        self.assertIn("Please choose a correct city value", profile_form.errors['city'])

    def test_returns_error_if_no_state_text_for_international_location(self):
        self.form_data['country'] = 'US'
        self.form_data['state_text'] = ''
        profile_form = ProfileSpecificRegistrationForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('state_text', profile_form.errors)
        self.assertIn("Please enter a value for state", profile_form.errors['state_text'])

    def test_returns_error_if_no_city_text_for_international_location(self):
        self.form_data['country'] = 'US'
        self.form_data['state_text'] = 'Ohio'
        self.form_data['city_text'] = ''
        profile_form = ProfileSpecificRegistrationForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('city_text', profile_form.errors)
        self.assertIn("Please enter a value for city", profile_form.errors['city_text'])

    def test_non_india_country_saved_correctly(self):
        self.assertTrue(self.profile_form_international.is_valid())
        user = self.profile_form_international.save()
        self.assertEqual(user.country, 'US')

    def test_state_saved_correctly_for_international_location(self):
        self.assertTrue(self.profile_form_international.is_valid())
        user = self.profile_form_international.save()
        self.assertIsNone(user.state)
        self.assertEqual(user.state_text, 'Ohio')

    def test_country_saved_correctly_for_international_location(self):
        self.assertTrue(self.profile_form_international.is_valid())
        user = self.profile_form_international.save()
        self.assertIsNone(user.city)
        self.assertEqual(user.city_text, 'xyz')

    def test_mobile_no_saved_correctly(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        self.assertEqual(user.mobile, self.form_data['mobile'])

    def test_display_pic_uploaded(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        display_picture_path = user.display_picture.path
        self.assertTrue(os.path.exists(display_picture_path))

    def test_cover_pic_uploaded(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        cover_picture_path = user.cover_picture.path
        self.assertTrue(os.path.exists(cover_picture_path))

    def test_registration_midout_unset(self):
        self.assertTrue(self.user.registration_midout)
        user = self.profile_form.save()
        self.assertEqual(user, self.user)
        self.assertFalse(user.registration_midout)


@pytest.mark.django_db
class TestChangePasswordForm(unittest.TestCase):

    def setUp(self):
        self.form_data = {
            'password1': 'dummy123',
            'password2': 'dummy123',
        }
        self.change_password_form = ChangePasswordForm(self.form_data)

    def test_instantiation(self):
        self.assertTrue(self.change_password_form)

    def test_form_valid(self):
        self.assertTrue(self.change_password_form.is_valid())

    def test_form_is_not_multipart(self):
        change_password_form = ChangePasswordForm()
        self.assertFalse(change_password_form.is_multipart())

    def test_form_invalid_if_password1_missing(self):
        del self.form_data['password1']
        change_password_form = ChangePasswordForm(self.form_data)
        self.assertFalse(change_password_form.is_valid())
        self.assertIn('password1', change_password_form.errors)
        self.assertIn('This field is required.', change_password_form.errors['password1'])

    def test_form_invalid_if_password2_missing(self):
        del self.form_data['password2']
        change_password_form = ChangePasswordForm(self.form_data)
        self.assertFalse(change_password_form.is_valid())
        self.assertIn('password2', change_password_form.errors)
        self.assertIn('This field is required.', change_password_form.errors['password2'])

    def test_form_invalid_if_passwords_do_not_match(self):
        self.form_data['password2'] = 'dummy'
        change_password_form = ChangePasswordForm(self.form_data)
        self.assertFalse(change_password_form.is_valid())
        self.assertIn('password1', change_password_form.errors)

    def test_form_invalid_if_password_less_than_6_characters(self):
        self.form_data['password1'] = 'abc'
        change_password_form = ChangePasswordForm(self.form_data)
        self.assertFalse(change_password_form.is_valid())
        self.assertIn('password1', change_password_form.errors)


@pytest.mark.django_db
class TestEditUserProfileForm(unittest.TestCase):

    def setUp(self):
        self.user = MidoutUserFactory()
        self.form_data = {
            'email' : self.user.email,
            'name': 'Jon Snow',
            'gender' : 'M',
            'date_of_birth':'12/15/2015',
            'country': 'IN',
            'state': '1013',
            'state_text': '',
            'city': '10178',
            'city_text': '',
            'mobile': '9999999999',
        }

        self.form_data_international = {
            'email' : self.user.email,
            'name': 'Jon Snow',
            'gender' : 'M',
            'date_of_birth':'12/15/2015',
            'country': 'US',
            'state': '',
            'state_text': 'Ohio',
            'city': '',
            'city_text': 'xyz',
            'mobile': '9999999999',
        }

        self.display_picture_path = 'accounts/tests/test_display_pic.png'
        self.cover_picture_path = 'accounts/tests/test_cover_pic.png'

        self.file_data = {
            'display_picture':SimpleUploadedFile(name='test_display_pic.png', content=open(self.display_picture_path, 'rb').read()),
            'cover_picture': SimpleUploadedFile(name='test_cover_pic.png', content=open(self.cover_picture_path, 'rb').read())
        }
        self.profile_form = EditUserProfileForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.profile_form_international = EditUserProfileForm(data=self.form_data_international, files=self.file_data, instance=self.user)

    def tearDown(self):
        """
        Delete the test uploads
        """
        shutil.rmtree(settings.IMAGE_UPLOAD_DIR, ignore_errors=True)

    def test_instantiation(self):
        self.assertTrue(self.profile_form)
        self.assertTrue(self.profile_form_international)

    def test_form_valid(self):
        self.assertTrue(self.profile_form.is_valid())
        self.assertTrue(self.profile_form_international.is_valid())

    def test_form_is_multipart(self):
        profile_form = EditUserProfileForm()
        self.assertTrue(profile_form.is_multipart())

    def test_email_cannot_be_edited(self):
        self.form_data['email'] = 'test@testing.com'
        profile_form = EditUserProfileForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('email', profile_form.errors)
        self.assertIn('Email cannot be edited', profile_form.errors['email'])

    def test_email_field_readonly(self):
        profile_form = EditUserProfileForm()
        self.assertTrue(profile_form.fields['email'].widget.attrs['readonly'])

    def test_name_can_be_edited(self):
        self.form_data['name'] = 'some name'
        profile_form = EditUserProfileForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertTrue(profile_form.is_valid())
        user = profile_form.save()
        self.assertEqual(user.name, self.form_data['name'])

    def test_name_must_be_full(self):
        self.form_data['name'] = 'Jon'
        profile_form = EditUserProfileForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('name', profile_form.errors)
        self.assertIn('Please enter full name.', profile_form.errors['name'])

    def test_gender_can_be_edited(self):
        self.form_data['gender'] = 'F'
        self.assertNotEqual(self.user.gender, self.form_data['gender'])
        profile_form = EditUserProfileForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertTrue(profile_form.is_valid())
        user = profile_form.save()
        self.assertEqual(self.user.gender, self.form_data['gender'])

    def test_display_pic_can_be_empty(self):
        self.file_data['display_picture'] = ''
        profile_form = EditUserProfileForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertTrue(profile_form.is_valid())

    def test_cover_pic_can_be_empty(self):
        self.file_data['cover_picture'] = ''
        profile_form = EditUserProfileForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertTrue(profile_form.is_valid())

    def test_image_file_must_be_opened_in_rb_mode(self):
        with self.assertRaises(UnicodeDecodeError):
            SimpleUploadedFile(name='test_display_pic.png', content=open(self.display_picture_path).read())

    def test_image_file_content_must_be_read(self):
        with self.assertRaises(TypeError):
            SimpleUploadedFile(name='test_display_pic.png', content=open(self.display_picture_path, 'rb'))

    def test_content_does_not_accepts_string_content_in_mock_image_file(self):
        with self.assertRaises(TypeError):
            SimpleUploadedFile(name='test_display_pic.png', content='some_content')

    def test_not_accepts_invalid_non_image_display_pic_file(self):
        self.file_data['display_picture'] = SimpleUploadedFile(name='test_views.py', content=open('accounts/tests/test_views.py', 'rb').read())
        profile_form = EditUserProfileForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('display_picture', profile_form.errors)

    def test_not_accepts_invalid_non_image_cover_pic_file(self):
        self.file_data['cover_picture'] = SimpleUploadedFile(name='test_views.py', content=open('accounts/tests/test_views.py', 'rb').read())
        profile_form = EditUserProfileForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('cover_picture', profile_form.errors)

    def test_date_of_birth_saved_correctly(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        self.assertEqual(user.date_of_birth.year, 2015)
        self.assertEqual(user.date_of_birth.month, 12)
        self.assertEqual(user.date_of_birth.day, 15)

    def test_gender_saved_correctly(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        self.assertEqual(user.gender, 'M')

    def test_country_saved_correctly(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        self.assertEqual(user.country, 'IN')

    def test_state_saved_correctly(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        self.assertEqual(user.state, 1013)
        self.assertEqual(user.state_text, '')

    def test_city_saved_correctly(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        self.assertEqual(user.city, 10178)
        self.assertEqual(user.city_text, '')

    def test_returns_error_if_no_state_for_india(self):
        self.form_data['state'] = ''
        profile_form = EditUserProfileForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('state', profile_form.errors)
        self.assertIn("Please choose a value for state", profile_form.errors['state'])

    def test_returns_error_if_no_city_for_india(self):
        self.form_data['city'] = ''
        profile_form = EditUserProfileForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('city', profile_form.errors)
        self.assertIn("Please choose a value for city", profile_form.errors['city'])

    def test_returns_error_if_city_of_different_state(self):
        self.form_data['city'] = 10050
        profile_form = EditUserProfileForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('city', profile_form.errors)
        self.assertIn("Please choose a correct city value", profile_form.errors['city'])

    def test_returns_error_if_no_state_text_for_international_location(self):
        self.form_data['country'] = 'US'
        self.form_data['state_text'] = ''
        profile_form = EditUserProfileForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('state_text', profile_form.errors)
        self.assertIn("Please enter a value for state", profile_form.errors['state_text'])

    def test_returns_error_if_no_city_text_for_international_location(self):
        self.form_data['country'] = 'US'
        self.form_data['state_text'] = 'Ohio'
        self.form_data['city_text'] = ''
        profile_form = EditUserProfileForm(data=self.form_data, files=self.file_data, instance=self.user)
        self.assertFalse(profile_form.is_valid())
        self.assertIn('city_text', profile_form.errors)
        self.assertIn("Please enter a value for city", profile_form.errors['city_text'])

    def test_non_india_country_saved_correctly(self):
        self.assertTrue(self.profile_form_international.is_valid())
        user = self.profile_form_international.save()
        self.assertEqual(user.country, 'US')

    def test_state_saved_correctly_for_international_location(self):
        self.assertTrue(self.profile_form_international.is_valid())
        user = self.profile_form_international.save()
        self.assertIsNone(user.state)
        self.assertEqual(user.state_text, 'Ohio')

    def test_country_saved_correctly_for_international_location(self):
        self.assertTrue(self.profile_form_international.is_valid())
        user = self.profile_form_international.save()
        self.assertIsNone(user.city)
        self.assertEqual(user.city_text, 'xyz')

    def test_mobile_no_saved_correctly(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        self.assertEqual(user.mobile, self.form_data['mobile'])

    def test_display_pic_uploaded(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        display_picture_path = user.display_picture.path
        self.assertTrue(os.path.exists(display_picture_path))

    def test_cover_pic_uploaded(self):
        self.assertTrue(self.profile_form.is_valid())
        user = self.profile_form.save()
        cover_picture_path = user.cover_picture.path
        self.assertTrue(os.path.exists(cover_picture_path))

    def test_registration_midout_unset(self):
        self.assertTrue(self.user.registration_midout)
        user = self.profile_form.save()
        self.assertEqual(user, self.user)
        self.assertFalse(user.registration_midout)

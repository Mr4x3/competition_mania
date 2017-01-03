# inbuilt python imports
import unittest
import os
import base64
import fudge
from datetime import datetime, timedelta

# inbuilt django imports
from django.test import Client
from django.db.utils import IntegrityError
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

# third-party django imports
import pytest
from Crypto.Cipher import XOR

# inter-app imports
from sportsvitae.shared.factories import UserFactory, MidoutUserFactory, CricketerFactory, FriendRequestFactory, MessageFactory, FriendRequestAcceptNotificationFactory, UserWallPostFactory

# local imports
from ..models import User, FriendRequest, Message
from ..utils import encode_token

@pytest.mark.django_db
class TestHomePageView(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.url = reverse('homepage')
        self.response = self.client.get(self.url)
        self.user = UserFactory()
        self.login_post_data = {
            'form_type' : 'login',
            'login-email': self.user.email,
            'login-password': settings.TEST_USER_PASSWORD
        }
        self.registration_post_data = {
            'form_type' : 'registration',
            'registration-email': 'dummy@dummy.com',
            'registration-password1': settings.TEST_USER_PASSWORD,
            'registration-password2': settings.TEST_USER_PASSWORD,
            'registration-name': 'Jon Snow',
            'registration-gender': 'M'
        }

    def test_returns_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_returns_correct_context_parameters(self):
        self.assertIn('login_form', self.response.context_data)
        self.assertIn('registration_form', self.response.context_data)

    def test_correct_template_used(self):
        self.assertIn('accounts/homepage.html', self.response.template_name)

    def test_user_logins_when_login_form_submitted(self):
        self.assertFalse(self.client.session.has_key('_auth_user_id'))
        response = self.client.post(self.url, self.login_post_data)
        self.assertTrue(self.client.session.has_key('_auth_user_id'))
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.id))

    def test_redirects_to_my_wall_on_login_if_reg_complete(self):
        response = self.client.post(self.url, self.login_post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace(settings.TEST_SERVER_DOMAIN, ''), reverse('my_wall'))

    def test_redirects_to_profile_specific_reg_on_login_if_reg_incomplete(self):
        User.objects.all().delete()
        self.user = MidoutUserFactory()
        self.login_post_data['login-email'] = self.user.email
        response = self.client.post(self.url, self.login_post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace(settings.TEST_SERVER_DOMAIN, ''), reverse('profile_specific_registration'))

    def test_redirects_to_next_url_if_login_successful(self):
        next_url = '/messages/'
        url = self.url + '?next=' + next_url
        response = self.client.post(url, self.login_post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace(settings.TEST_SERVER_DOMAIN, ''), next_url)

    def test_returns_both_forms_in_context_if_error_in_login_form(self):
        del self.login_post_data['login-email']
        response = self.client.post(self.url, self.login_post_data)
        self.assertIn('login_form', response.context)
        self.assertIn('registration_form', response.context)

    def test_only_login_form_bound_in_case_of_login_form_error(self):
        del self.login_post_data['login-email']
        response = self.client.post(self.url, self.login_post_data)
        self.assertTrue(response.context['login_form'].is_bound)
        self.assertFalse(response.context['registration_form'].is_bound)

    def test_returns_error_if_login_form_email_missing(self):
        del self.login_post_data['login-email']
        response = self.client.post(self.url, self.login_post_data)
        self.assertIn('login_form', response.context)
        self.assertFalse(response.context['login_form'].is_valid())

    def test_returns_error_if_login_form_password_missing(self):
        del self.login_post_data['login-password']
        response = self.client.post(self.url, self.login_post_data)
        self.assertIn('login_form', response.context)
        self.assertFalse(response.context['login_form'].is_valid())

    def test_returns_error_if_login_form_email_id_invalid(self):
        self.login_post_data['login-email'] = 'dummy'
        response = self.client.post(self.url, self.login_post_data)
        self.assertIn('login_form', response.context)
        self.assertFalse(response.context['login_form'].is_valid())

    def test_returns_error_if_login_form_password_value_invalid(self):
        self.login_post_data['login-password'] = 'dummy'
        response = self.client.post(self.url, self.login_post_data)
        self.assertIn('login_form', response.context)
        self.assertFalse(response.context['login_form'].is_valid())

    def test_user_created_on_registration(self):
        self.assertFalse(User.objects.filter(email=self.registration_post_data['registration-email']).exists())
        response = self.client.post(self.url, self.registration_post_data)
        self.assertTrue(User.objects.filter(email=self.registration_post_data['registration-email']).exists())

    @fudge.patch('accounts.views.send_email_verification_mail')
    def test_verification_mail_sent(self, mock_send_email):
        mock_send_email.expects_call()
        response = self.client.post(self.url, self.registration_post_data)

    def test_user_loggedin_on_registration(self):
        self.assertFalse(self.client.session.has_key('_auth_user_id'))
        response = self.client.post(self.url, self.registration_post_data)
        self.assertTrue(self.client.session.has_key('_auth_user_id'))
        created_user = User.objects.get(email=self.registration_post_data['registration-email'])
        self.assertEqual(self.client.session['_auth_user_id'], str(created_user.id))

    def test_redirects_to_profile_registration_on_registration(self):
        response = self.client.post(self.url, self.registration_post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace(settings.TEST_SERVER_DOMAIN, ''), reverse('profile_specific_registration'))

    def test_returns_both_forms_in_context_if_error_in_registration_form(self):
        self.registration_post_data['registration-email'] = self.user.email
        response = self.client.post(self.url, self.registration_post_data)
        self.assertIn('registration_form', response.context)
        self.assertIn('login_form', response.context)

    def test_only_registration_form_bound_in_case_of_registration_form_error(self):
        self.registration_post_data['registration-email'] = self.user.email
        response = self.client.post(self.url, self.registration_post_data)
        self.assertTrue(response.context['registration_form'].is_bound)
        self.assertFalse(response.context['login_form'].is_bound)

    def test_returns_error_if_same_email_exists_in_registration(self):
        self.registration_post_data['registration-email'] = self.user.email
        response = self.client.post(self.url, self.registration_post_data)
        self.assertIn('registration_form', response.context)
        self.assertFalse(response.context['registration_form'].is_valid())

    def test_returns_error_if_password_less_than_6_characters_in_registration(self):
        self.registration_post_data['registration-password1'] = 'abc'
        response = self.client.post(self.url, self.registration_post_data)
        self.assertIn('registration_form', response.context)
        self.assertFalse(response.context['registration_form'].is_valid())

    def test_returns_error_if_no_email_in_registration(self):
        del self.registration_post_data['registration-email']
        response = self.client.post(self.url, self.registration_post_data)
        self.assertIn('registration_form', response.context)
        self.assertFalse(response.context['registration_form'].is_valid())

    def test_returns_error_if_no_password1_in_registration(self):
        del self.registration_post_data['registration-password1']
        response = self.client.post(self.url, self.registration_post_data)
        self.assertIn('registration_form', response.context)
        self.assertFalse(response.context['registration_form'].is_valid())

    def test_returns_error_if_no_password2_in_registration(self):
        del self.registration_post_data['registration-password2']
        response = self.client.post(self.url, self.registration_post_data)
        self.assertIn('registration_form', response.context)
        self.assertFalse(response.context['registration_form'].is_valid())

    def test_returns_error_if_no_gender_in_registration(self):
        del self.registration_post_data['registration-gender']
        response = self.client.post(self.url, self.registration_post_data)
        self.assertIn('registration_form', response.context)
        self.assertFalse(response.context['registration_form'].is_valid())

    def test_returns_error_if_no_name_in_registration(self):
        del self.registration_post_data['registration-name']
        response = self.client.post(self.url, self.registration_post_data)
        self.assertIn('registration_form', response.context)
        self.assertFalse(response.context['registration_form'].is_valid())

    def test_returns_error_if_passwords_do_not_match_in_registration(self):
        self.registration_post_data['registration-password2'] = 'dummy'
        response = self.client.post(self.url, self.registration_post_data)
        self.assertIn('registration_form', response.context)
        self.assertFalse(response.context['registration_form'].is_valid())

    def test_returns_error_if_no_last_name_in_registration(self):
        self.registration_post_data['registration-name'] = 'Jon'
        response = self.client.post(self.url, self.registration_post_data)
        self.assertIn('registration_form', response.context)
        self.assertFalse(response.context['registration_form'].is_valid())

    def test_returns_error_if_first_name_with_dot_in_registration(self):
        self.registration_post_data['registration-name'] = 'Jon.'
        response = self.client.post(self.url, self.registration_post_data)
        self.assertIn('registration_form', response.context)
        self.assertFalse(response.context['registration_form'].is_valid())

    def test_user_created_on_registration_if_name_separated_by_dot(self):
        self.registration_post_data['registration-name'] = 'Jon.Snow'
        self.assertFalse(User.objects.filter(email=self.registration_post_data['registration-email']).exists())
        response = self.client.post(self.url, self.registration_post_data)
        self.assertTrue(User.objects.filter(email=self.registration_post_data['registration-email']).exists())


@pytest.mark.django_db
class TestProfileSpecificRegistrationView(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = MidoutUserFactory()
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('profile_specific_registration')
        self.response = self.client.get(self.url)

        self.display_picture_path = 'accounts/tests/test_display_pic.png'
        self.cover_picture_path = 'accounts/tests/test_cover_pic.png'

        self.display_picture = SimpleUploadedFile(name='test_display_pic.png', content=open(self.display_picture_path, 'rb').read())
        self.cover_picture = SimpleUploadedFile(name='test_cover_pic.png', content=open(self.cover_picture_path, 'rb').read())

        self.base64_display_picture = 'data:image/png;base64,' + base64.urlsafe_b64encode(self.display_picture.read()).decode('utf-8')
        self.base64_cover_picture = 'data:image/png;base64,' + base64.urlsafe_b64encode(self.cover_picture.read()).decode('utf-8')

        self.post_data = {
            'email' : self.user.email,
            'name': self.user.name,
            'date_of_birth':'12/15/2015',
            'gender': 'M',
            'country': 'IN',
            'state': '1013',
            'state_text': '',
            'city': '10178',
            'city_text': '',
            'mobile': '9999999999',
            'display_picture': self.base64_display_picture,
            'cover_picture': self.base64_cover_picture,
        }

        self.post_data_international = {
            'email' : self.user.email,
            'name': self.user.name,
            'date_of_birth':'12/15/2015',
            'gender': 'M',
            'country': 'US',
            'state': '',
            'state_text': 'Ohio',
            'city': '',
            'city_text': 'xyz',
            'mobile': '9999999999',
            'display_picture': self.base64_display_picture,
            'cover_picture': self.base64_cover_picture,
        }

    def test_returns_200_response_on_get(self):
        self.assertEqual(self.response.status_code, 200)

    def test_redirects_to_homepage_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '').split('?next=')[0]
        self.assertEqual(response_url, reverse('homepage'))

    def test_redirects_to_verify_email_page_if_email_not_verified(self):
        self.user.is_email_verified = False
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('verify_email'))

    def test_user_redirects_to_sports_specific_registration_if_not_midout(self):
        User.objects.all().delete()
        user = UserFactory()
        self.client.login(username=user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('cricket_profile_registration'))

    def test_user_redirects_to_my_wall_if_complete_sports_user(self):
        User.objects.all().delete()
        cricketer = CricketerFactory()
        self.client.login(username=cricketer.user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('my_wall'))

    def test_correct_template_used(self):
        self.assertIn('accounts/profile_specific_registration.html', self.response.template_name)

    def test_form_has_instance_set(self):
        self.assertTrue(self.response.context_data['form'].instance)
        self.assertEqual(self.response.context_data['form'].instance, self.user)

    def test_form_has_name_in_initial(self):
        form_initial = self.response.context_data['form'].initial
        self.assertEqual(form_initial['name'], self.user.name)

    def test_redirects_to_sports_registration_on_post_success(self):
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace(settings.TEST_SERVER_DOMAIN, ''), reverse('cricket_profile_registration'))

    def test_user_updated_on_success(self):
        old_last_modified = self.user.last_modified
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        self.assertNotEqual(user.last_modified, old_last_modified)

    def test_email_cannot_be_edited(self):
        self.post_data['email'] = 'test@testing.com'
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(response.context_data['form'].is_valid())
        self.assertIn('email', response.context_data['form'].errors)

    def test_name_can_be_edited(self):
        self.post_data['name'] = 'some name'
        self.assertNotEqual(self.user.name, self.post_data['name'])
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.name, self.post_data['name'])

    def test_name_must_be_full(self):
        self.post_data['name'] = 'Jon'
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(response.context_data['form'].is_valid())
        self.assertIn('name', response.context_data['form'].errors)

    def test_gender_can_be_edited(self):
        self.post_data['gender'] = 'F'
        self.assertNotEqual(self.user.name, self.post_data['gender'])
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.gender, self.post_data['gender'])

    def test_display_pic_can_be_empty(self):
        self.post_data['display_picture'] = ''
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace(settings.TEST_SERVER_DOMAIN, ''), reverse('cricket_profile_registration'))

    def test_cover_pic_can_be_empty(self):
        self.post_data['cover_picture'] = ''
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace(settings.TEST_SERVER_DOMAIN, ''), reverse('cricket_profile_registration'))

    def test_date_of_birth_saved_correctly(self):
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        expected_date = datetime(2015, 12, 15, 0, 0) - timedelta(hours=5, minutes=30)
        self.assertEqual(user.date_of_birth.year, expected_date.year)
        self.assertEqual(user.date_of_birth.month, expected_date.month)
        self.assertEqual(user.date_of_birth.day, expected_date.day)

    def test_country_saved_correctly(self):
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.country, 'IN')

    def test_state_saved_correctly(self):
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.state, 1013)
        self.assertEqual(user.state_text, '')

    def test_city_saved_correctly(self):
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.city, 10178)
        self.assertEqual(user.city_text, '')

    def test_returns_error_if_no_state_for_india(self):
        self.post_data['state'] = ''
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(response.context_data['form'].is_valid())
        self.assertIn('state', response.context_data['form'].errors)

    def test_returns_error_if_no_city_for_india(self):
        self.post_data['city'] = ''
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(response.context_data['form'].is_valid())
        self.assertIn('city', response.context_data['form'].errors)

    def test_returns_error_if_no_state_text_for_international_location(self):
        self.post_data['country'] = 'US'
        self.post_data['state_text'] = ''
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(response.context_data['form'].is_valid())
        self.assertIn('state_text', response.context_data['form'].errors)

    def test_returns_error_if_no_city_text_for_international_location(self):
        self.post_data['country'] = 'US'
        self.post_data['state_text'] = 'Ohio'
        self.post_data['city_text'] = ''
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(response.context_data['form'].is_valid())
        self.assertIn('city_text', response.context_data['form'].errors)

    def test_non_india_country_saved_correctly(self):
        response = self.client.post(self.url, self.post_data_international)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.country, 'US')

    def test_state_saved_correctly_for_international_location(self):
        response = self.client.post(self.url, self.post_data_international)
        user = User.objects.get(id=self.user.id)
        self.assertIsNone(user.state)
        self.assertEqual(user.state_text, 'Ohio')

    def test_country_saved_correctly_for_international_location(self):
        response = self.client.post(self.url, self.post_data_international)
        user = User.objects.get(id=self.user.id)
        self.assertIsNone(user.city)
        self.assertEqual(user.city_text, 'xyz')

    def test_mobile_no_saved_correctly(self):
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.mobile, self.post_data['mobile'])

    def test_display_pic_uploaded(self):
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        display_picture_path = user.display_picture.path
        self.assertTrue(os.path.exists(display_picture_path))

    def test_cover_pic_uploaded(self):
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        cover_picture_path = user.cover_picture.path
        self.assertTrue(os.path.exists(cover_picture_path))

    def test_returns_no_error_if_both_pictures_empty(self):
        self.post_data['display_picture'] = ''
        self.post_data['cover_picture'] = ''
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace(settings.TEST_SERVER_DOMAIN, ''), reverse('cricket_profile_registration'))
        user = User.objects.get(id=self.user.id)
        self.assertRaises(ValueError, getattr, user.display_picture, 'file')
        self.assertRaises(ValueError, getattr, user.cover_picture, 'file')


@pytest.mark.django_db
class TestLoginView(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.url = '/login/'

        self.login_post_data = {
            'email': self.user.email,
            'password': settings.TEST_USER_PASSWORD
        }

    def test_returns_200_response(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        response = self.client.get(self.url)
        self.assertIn('accounts/login.html', response.template_name)

    def test_user_logins_when_login_form_submitted(self):
        self.assertFalse(self.client.session.has_key('_auth_user_id'))
        response = self.client.post(self.url, self.login_post_data)
        self.assertTrue(self.client.session.has_key('_auth_user_id'))
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.id))

    def test_redirects_to_my_wall_on_login_if_reg_complete(self):
        response = self.client.post(self.url, self.login_post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace(settings.TEST_SERVER_DOMAIN, ''), reverse('my_wall'))

    def test_redirects_to_next_url_if_login_successful(self):
        next_url = '/messages/'
        url = self.url + '?next=' + next_url
        response = self.client.post(url, self.login_post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace(settings.TEST_SERVER_DOMAIN, ''), next_url)

    def test_returns_error_if_login_form_email_missing(self):
        del self.login_post_data['email']
        response = self.client.post(self.url, self.login_post_data)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())

    def test_returns_error_if_login_form_password_missing(self):
        del self.login_post_data['password']
        response = self.client.post(self.url, self.login_post_data)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())

    def test_returns_error_if_login_form_email_id_invalid(self):
        self.login_post_data['email'] = 'dummy'
        response = self.client.post(self.url, self.login_post_data)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())

    def test_returns_error_if_login_form_password_value_invalid(self):
        self.login_post_data['password'] = 'dummy'
        response = self.client.post(self.url, self.login_post_data)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())


@pytest.mark.django_db
class TestLogoutView(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        self.url = '/logout/'

        self.login_post_data = {
            'email': self.user.email,
            'password': settings.TEST_USER_PASSWORD
        }

    def test_returns_200_response(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_correct_template_used(self):
        response = self.client.get(self.url)
        self.assertIn('accounts/logout.html', response.template_name)

    def test_logouts_user(self):
        self.assertTrue(self.client.session.has_key('_auth_user_id'))
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.id))
        response = self.client.get(self.url)
        self.assertFalse(self.client.session.has_key('_auth_user_id'))

    def test_user_logins_when_login_form_submitted(self):
        self.client.get(self.url)
        self.assertFalse(self.client.session.has_key('_auth_user_id'))
        response = self.client.post(self.url, self.login_post_data)
        self.assertTrue(self.client.session.has_key('_auth_user_id'))
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.id))

    def test_redirects_to_my_wall_on_login_if_reg_complete(self):
        response = self.client.post(self.url, self.login_post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace(settings.TEST_SERVER_DOMAIN, ''), reverse('my_wall'))

    def test_redirects_to_next_url_if_login_successful(self):
        next_url = '/messages/'
        url = self.url + '?next=' + next_url
        response = self.client.post(url, self.login_post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace(settings.TEST_SERVER_DOMAIN, ''), next_url)

    def test_returns_error_if_login_form_email_missing(self):
        del self.login_post_data['email']
        response = self.client.post(self.url, self.login_post_data)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())

    def test_returns_error_if_login_form_password_missing(self):
        del self.login_post_data['password']
        response = self.client.post(self.url, self.login_post_data)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())

    def test_returns_error_if_login_form_email_id_invalid(self):
        self.login_post_data['email'] = 'dummy'
        response = self.client.post(self.url, self.login_post_data)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())

    def test_returns_error_if_login_form_password_value_invalid(self):
        self.login_post_data['password'] = 'dummy'
        response = self.client.post(self.url, self.login_post_data)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())


@pytest.mark.django_db
class TestConnectRequestsView(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CricketerFactory().user
        self.friend1 = CricketerFactory().user
        self.friend2 = CricketerFactory().user
        self.user.add_friend(self.friend1)
        self.user.add_friend(self.friend2)
        self.friend_request1 = FriendRequestFactory(from_user=self.friend1, to_user=self.user)
        self.friend_request2 = FriendRequestFactory(from_user=self.friend2, to_user=self.user)
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('pending_friend_requests')
        self.response = self.client.get(self.url)

    def test_returns_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_returns_correct_context_parameters(self):
        self.assertIn('pending_friend_requests', self.response.context_data)

    def test_returns_friends_requests_in_context(self):
        self.assertIn(self.friend_request1, self.response.context_data['pending_friend_requests'])
        self.assertIn(self.friend_request2, self.response.context_data['pending_friend_requests'])

    def test_returns_friends_requests_sorted_by_latest_first(self):
        friend_requests = self.response.context_data['pending_friend_requests']
        self.assertEqual(friend_requests, [self.friend_request2, self.friend_request1])

    def test_does_not_return_accepted_friend_requests(self):
        self.friend_request1.accepted = True
        self.friend_request1.save()
        response = self.client.get(self.url)
        friend_requests = response.context_data['pending_friend_requests']
        self.assertEqual(friend_requests, [self.friend_request2])

    def test_returns_friend_requests_sorted_by_not_viewed_first(self):
        FriendRequest.objects.all().delete()
        friend_request1 = FriendRequestFactory(from_user=self.friend1, to_user=self.user)
        friend_request2 = FriendRequestFactory(from_user=self.friend2, to_user=self.user, viewed=True)
        response = self.client.get(self.url)
        friend_requests = response.context_data['pending_friend_requests']
        self.assertEqual(friend_requests, [friend_request1, friend_request2])

    def test_correct_template_used(self):
        self.assertIn('accounts/pending_friend_requests.html', self.response.template_name)

    def test_redirects_to_homepage_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '').split('?next=')[0]
        self.assertEqual(response_url, reverse('homepage'))

    def test_redirects_to_verify_email_page_if_email_not_verified(self):
        self.user.is_email_verified = False
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('verify_email'))

    def test_user_redirects_to_profile_reg_if_registration_midout(self):
        User.objects.all().delete()
        user = MidoutUserFactory()
        self.client.login(username=user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse_lazy('profile_specific_registration'))

    def test_user_redirects_to_sports_profile_registration_if_no_sports_profile(self):
        User.objects.all().delete()
        user = UserFactory()
        self.client.login(username=user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('cricket_profile_registration'))


@pytest.mark.django_db
class TestConnectionsView(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.cricketer = CricketerFactory()
        self.friend1 = CricketerFactory()
        self.friend2 = CricketerFactory()
        self.cricketer.user.add_friend(self.friend1.user)
        self.cricketer.user.add_friend(self.friend2.user)
        self.client.login(username=self.cricketer.user.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('connections')
        self.response = self.client.get(self.url)

    def test_returns_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_returns_correct_context_parameters(self):
        self.assertIn('friends', self.response.context_data)

    def test_returns_friends_in_context(self):
        self.assertIn(self.friend1.user, self.response.context_data['friends'])
        self.assertIn(self.friend2.user, self.response.context_data['friends'])

    def test_correct_template_used(self):
        self.assertIn('accounts/my_connections.html', self.response.template_name)

    def test_redirects_to_homepage_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '').split('?next=')[0]
        self.assertEqual(response_url, reverse('homepage'))

    def test_redirects_to_verify_email_page_if_email_not_verified(self):
        self.cricketer.user.is_email_verified = False
        self.cricketer.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('verify_email'))

    def test_user_redirects_to_profile_reg_if_registration_midout(self):
        User.objects.all().delete()
        user = MidoutUserFactory()
        self.client.login(username=user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse_lazy('profile_specific_registration'))

    def test_user_redirects_to_sports_profile_registration_if_no_sports_profile(self):
        User.objects.all().delete()
        user = UserFactory()
        self.client.login(username=user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('cricket_profile_registration'))


@pytest.mark.django_db
class TestUserMessagesView(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.cricketer = CricketerFactory()
        self.sender = self.cricketer.user
        # self.friend1 = CricketerFactory()
        # self.friend2 = CricketerFactory()
        # self.cricketer.user.add_friend(self.friend1.user)
        # self.cricketer.user.add_friend(self.friend2.user)
        self.client.login(username=self.sender.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('user_messages')
        self.response = self.client.get(self.url)

        self.sender = CricketerFactory().user
        # self.recipient = CricketerFactory().user
        # self.post_data = {
        #     'sender' : self.sender.id,
        #     'recipient' : self.recipient.id,
        #     'text': 'Hello'
        # }

    def test_returns_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_correct_template_used(self):
        self.assertIn('accounts/user_messages.html', self.response.template_name)

    def test_redirects_to_homepage_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '').split('?next=')[0]
        self.assertEqual(response_url, reverse('homepage'))

    def test_redirects_to_verify_email_page_if_email_not_verified(self):
        self.sender.is_email_verified = False
        self.sender.save()
        self.client.session.flush()
        self.client.login(username=self.sender.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('verify_email'))

    def test_user_redirects_to_profile_reg_if_registration_midout(self):
        User.objects.all().delete()
        user = MidoutUserFactory()
        self.client.login(username=user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse_lazy('profile_specific_registration'))

    def test_user_redirects_to_sports_profile_registration_if_no_sports_profile(self):
        User.objects.all().delete()
        user = UserFactory()
        self.client.login(username=user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('cricket_profile_registration'))

    def test_returns_correct_context_parameters(self):
        self.assertIn('all_friends_messaged', self.response.context_data)
        self.assertIn('last_messaged_friend_messages', self.response.context_data)


@pytest.mark.django_db
class TestFriendMessagesView(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CricketerFactory().user
        self.friend = CricketerFactory().user
        self.user.add_friend(self.friend)
        self.message = MessageFactory(sender=self.friend, recipient=self.user)
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('friend_messages', kwargs={'slug': self.friend.slug})

        self.response = self.client.get(self.url)

    def test_returns_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_correct_template_used(self):
        self.assertIn('accounts/user_messages.html', self.response.template_name)

    def test_returns_404_if_not_found(self):
        self.url = reverse('friend_messages', kwargs={'slug': 'aaa'})
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 404)

    def test_redirects_to_homepage_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '').split('?next=')[0]
        self.assertEqual(response_url, reverse('homepage'))

    def test_redirects_to_verify_email_page_if_email_not_verified(self):
        self.user.is_email_verified = False
        self.user.save()
        self.client.session.flush()
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('verify_email'))

    def test_user_redirects_to_profile_reg_if_registration_midout(self):
        User.objects.all().delete()
        user = MidoutUserFactory()
        self.client.login(username=user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse_lazy('profile_specific_registration'))

    def test_user_redirects_to_sports_profile_registration_if_no_sports_profile(self):
        User.objects.all().delete()
        user = UserFactory()
        self.client.login(username=user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('cricket_profile_registration'))

    def test_user_redirects_to_user_messages_if_no_chat_history(self):
        Message.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('user_messages'))

    def test_returns_correct_context_parameters(self):
        self.assertIn('all_friends_messaged', self.response.context_data)
        self.assertIn('clicked_friend_messages', self.response.context_data)


@pytest.mark.django_db
class TestEmailVerificationView(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = UserFactory(is_email_verified=False)
        self.token = encode_token(self.user.email, 1)
        self.url = reverse('email_verification', kwargs={'token': self.token})
        self.response = self.client.get(self.url)

        # Prepare Expired token
        self.token_expiry_date = datetime(2011, 1, 1, 0, 0)
        self.input_string = '{salt}|{email}|{token_type}|{token_expiry_date}'.format(salt=settings.TOKEN_ENCODE_SALT, email=self.user.email, token_type=0, token_expiry_date=self.token_expiry_date)
        self.xor_cipher = XOR.new(key=settings.TOKEN_ENCODE_SALT)
        self.expired_token = self.xor_cipher.encrypt(plaintext=bytes(self.input_string, 'utf-8') )
        self.expired_token = base64.urlsafe_b64encode(self.expired_token).decode('utf-8')

    def test_returns_302_response(self):
        self.assertEqual(self.response.status_code, 302)

    def test_redirects_to_profile_specific_registration_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('profile_specific_registration'))

    def test_user_gets_loggedin(self):
        self.client.session.flush()
        response = self.client.get(self.url)
        self.assertTrue(self.client.session.has_key('_auth_user_id'))
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.id))

    def test_sets_is_email_verified_flag(self):
        self.assertFalse(self.user.is_email_verified)
        response = self.client.get(self.url)
        self.user = User.objects.get(id=self.user.id)
        self.assertTrue(self.user.is_email_verified)

    def test_redirects_to_homepage_if_invalid_token(self):
        token = encode_token('a@a.com', 1)
        url = reverse('email_verification', kwargs={'token': token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('homepage'))

    def test_redirects_to_homepage_if_expired_token(self):
        url = reverse('email_verification', kwargs={'token': self.expired_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('homepage'))

    def test_message_for_email_verification_set(self):
        response = self.client.get(self.url)
        mail_verification_message = 'Your email has been successfully verified.'
        self.assertIn(mail_verification_message, self.client.cookies['messages'].value)


@pytest.mark.django_db
class TestVerifyEmailPage(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = UserFactory(is_email_verified=False)
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('verify_email')
        self.response = self.client.get(self.url)

    def test_returns_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_correct_template_used(self):
        self.assertIn('accounts/verify_email.html', self.response.template_name)

    def test_redirects_to_profile_specific_registration_page_if_email_already_verified(self):
        self.user.is_email_verified = True
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('profile_specific_registration'))

    def test_redirects_to_homepage_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '').split('?next=')[0]
        self.assertEqual(response_url, reverse('homepage'))


@pytest.mark.django_db
class TestChangePasswordView(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.token = encode_token(self.user.email, 1)
        self.url = reverse('change_password', kwargs={'token': self.token})
        self.response = self.client.get(self.url)

        # Prepare Expired token
        self.token_expiry_date = datetime(2011, 1, 1, 0, 0)
        self.input_string = '{salt}|{email}|{token_type}|{token_expiry_date}'.format(salt=settings.TOKEN_ENCODE_SALT, email=self.user.email, token_type=0, token_expiry_date=self.token_expiry_date)
        self.xor_cipher = XOR.new(key=settings.TOKEN_ENCODE_SALT)
        self.expired_token = self.xor_cipher.encrypt(plaintext=bytes(self.input_string, 'utf-8') )
        self.expired_token = base64.urlsafe_b64encode(self.expired_token).decode('utf-8')

        self.post_data = {
            'password1': 'dummy123',
            'password2': 'dummy123',
        }

    def test_returns_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_correct_template_used(self):
        self.assertIn('accounts/change_password.html', self.response.template_name)

    def test_user_gets_loggedin(self):
        self.client.session.flush()
        response = self.client.get(self.url)
        self.assertTrue(self.client.session.has_key('_auth_user_id'))
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.id))

    def test_redirects_to_homepage_if_invalid_token(self):
        token = encode_token('a@a.com', 1)
        url = reverse('email_verification', kwargs={'token': token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('homepage'))

    def test_redirects_to_homepage_if_expired_token(self):
        url = reverse('email_verification', kwargs={'token': self.expired_token})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('homepage'))

    def test_user_password_changed_successfully(self):
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.post(self.url, self.post_data)
        self.client.session.flush()
        self.assertFalse(self.client.session.has_key('_auth_user_id'))
        self.client.login(username=self.user.email, password=self.post_data['password1'])
        self.assertTrue(self.client.session.has_key('_auth_user_id'))
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.id))

    def test_user_cannot_login_with_old_password_on_success(self):
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        self.assertTrue(self.client.session.has_key('_auth_user_id'))
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.id))
        response = self.client.post(self.url, self.post_data)
        self.client.session.flush()
        self.assertFalse(self.client.session.has_key('_auth_user_id'))
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        self.assertFalse(self.client.session.has_key('_auth_user_id'))

    def test_message_for_password_success_set(self):
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.post(self.url, self.post_data)
        mail_verification_message = 'Your password has been successfully changed.'
        self.assertIn(mail_verification_message, self.client.cookies['messages'].value)

    def test_redirects_to_homepage_on_success(self):
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('my_wall'))


@pytest.mark.django_db
class TestEditUserProfileView(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.cricketer = CricketerFactory()
        self.user = self.cricketer.user
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('edit_user_profile')
        self.response = self.client.get(self.url)

        self.display_picture_path = 'accounts/tests/test_display_pic.png'
        self.cover_picture_path = 'accounts/tests/test_cover_pic.png'

        self.display_picture = SimpleUploadedFile(name='test_display_pic.png', content=open(self.display_picture_path, 'rb').read())
        self.cover_picture = SimpleUploadedFile(name='test_cover_pic.png', content=open(self.cover_picture_path, 'rb').read())

        self.post_data = {
            'email' : self.user.email,
            'name': self.user.name,
            'date_of_birth':'12/15/2015',
            'gender': 'M',
            'country': 'IN',
            'state': '1013',
            'state_text': '',
            'city': '10178',
            'city_text': '',
            'mobile': '9999999999',
            'display_picture': self.display_picture,
            'cover_picture': self.cover_picture,
        }

        self.post_data_international = {
            'email' : self.user.email,
            'name': self.user.name,
            'date_of_birth':'12/15/2015',
            'gender': 'M',
            'country': 'US',
            'state': '',
            'state_text': 'Ohio',
            'city': '',
            'city_text': 'xyz',
            'mobile': '9999999999',
            'display_picture': self.display_picture,
            'cover_picture': self.cover_picture,
        }

    def test_returns_200_response_on_get(self):
        self.assertEqual(self.response.status_code, 200)

    def test_redirects_to_homepage_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '').split('?next=')[0]
        self.assertEqual(response_url, reverse('homepage'))

    def test_redirects_to_verify_email_page_if_email_not_verified(self):
        self.user.is_email_verified = False
        self.user.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('verify_email'))

    def test_user_redirects_to_profile_reg_if_registration_midout(self):
        User.objects.all().delete()
        user = MidoutUserFactory()
        self.client.login(username=user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse_lazy('profile_specific_registration'))

    def test_user_redirects_to_sports_specific_registration_if_not_midout(self):
        User.objects.all().delete()
        user = UserFactory()
        self.client.login(username=user.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        response_url = response.url.replace(settings.TEST_SERVER_DOMAIN, '')
        self.assertEqual(response_url, reverse('cricket_profile_registration'))

    def test_correct_template_used(self):
        self.assertIn('accounts/edit_user_profile.html', self.response.template_name)

    def test_returns_latest_messages_and_requests_as_global_context_parameters(self):
        self.assertIn('latest_friend_requests', self.response.context)
        self.assertIn('latest_received_messages', self.response.context)

    def test_form_has_instance_set(self):
        self.assertTrue(self.response.context_data['form'].instance)
        self.assertEqual(self.response.context_data['form'].instance, self.user)

    def test_form_has_name_in_initial(self):
        form_initial = self.response.context_data['form'].initial
        self.assertEqual(form_initial['name'], self.user.name)

    def test_redirects_to_my_wall_on_post_success(self):
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace(settings.TEST_SERVER_DOMAIN, ''), reverse('my_wall'))

    def test_user_updated_on_success(self):
        old_last_modified = self.user.last_modified
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        self.assertNotEqual(user.last_modified, old_last_modified)

    def test_email_cannot_be_edited(self):
        self.post_data['email'] = 'test@testing.com'
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(response.context_data['form'].is_valid())
        self.assertIn('email', response.context_data['form'].errors)

    def test_name_can_be_edited(self):
        self.post_data['name'] = 'some name'
        self.assertNotEqual(self.user.name, self.post_data['name'])
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.name, self.post_data['name'])

    def test_name_must_be_full(self):
        self.post_data['name'] = 'Jon'
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(response.context_data['form'].is_valid())
        self.assertIn('name', response.context_data['form'].errors)

    def test_gender_can_be_edited(self):
        self.post_data['gender'] = 'F'
        self.assertNotEqual(self.user.name, self.post_data['gender'])
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.gender, self.post_data['gender'])

    def test_display_pic_can_be_empty(self):
        self.post_data['display_picture'] = ''
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace(settings.TEST_SERVER_DOMAIN, ''), reverse('my_wall'))

    def test_cover_pic_can_be_empty(self):
        self.post_data['cover_picture'] = ''
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url.replace(settings.TEST_SERVER_DOMAIN, ''), reverse('my_wall'))

    def test_date_of_birth_saved_correctly(self):
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        expected_date = datetime(2015, 12, 15, 0, 0) - timedelta(hours=5, minutes=30)
        self.assertEqual(user.date_of_birth.year, expected_date.year)
        self.assertEqual(user.date_of_birth.month, expected_date.month)
        self.assertEqual(user.date_of_birth.day, expected_date.day)

    def test_country_saved_correctly(self):
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.country, 'IN')

    def test_state_saved_correctly(self):
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.state, 1013)
        self.assertEqual(user.state_text, '')

    def test_city_saved_correctly(self):
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.city, 10178)
        self.assertEqual(user.city_text, '')

    def test_returns_error_if_no_state_for_india(self):
        self.post_data['state'] = ''
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(response.context_data['form'].is_valid())
        self.assertIn('state', response.context_data['form'].errors)

    def test_returns_error_if_no_city_for_india(self):
        self.post_data['city'] = ''
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(response.context_data['form'].is_valid())
        self.assertIn('city', response.context_data['form'].errors)

    def test_returns_error_if_no_state_text_for_international_location(self):
        self.post_data['country'] = 'US'
        self.post_data['state_text'] = ''
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(response.context_data['form'].is_valid())
        self.assertIn('state_text', response.context_data['form'].errors)

    def test_returns_error_if_no_city_text_for_international_location(self):
        self.post_data['country'] = 'US'
        self.post_data['state_text'] = 'Ohio'
        self.post_data['city_text'] = ''
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(response.context_data['form'].is_valid())
        self.assertIn('city_text', response.context_data['form'].errors)

    def test_non_india_country_saved_correctly(self):
        response = self.client.post(self.url, self.post_data_international)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.country, 'US')

    def test_state_saved_correctly_for_international_location(self):
        response = self.client.post(self.url, self.post_data_international)
        user = User.objects.get(id=self.user.id)
        self.assertIsNone(user.state)
        self.assertEqual(user.state_text, 'Ohio')

    def test_country_saved_correctly_for_international_location(self):
        response = self.client.post(self.url, self.post_data_international)
        user = User.objects.get(id=self.user.id)
        self.assertIsNone(user.city)
        self.assertEqual(user.city_text, 'xyz')

    def test_mobile_no_saved_correctly(self):
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        self.assertEqual(user.mobile, self.post_data['mobile'])

    def test_display_pic_uploaded(self):
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        display_picture_path = user.display_picture.path
        self.assertTrue(os.path.exists(display_picture_path))

    def test_cover_pic_uploaded(self):
        response = self.client.post(self.url, self.post_data)
        user = User.objects.get(id=self.user.id)
        cover_picture_path = user.cover_picture.path
        self.assertTrue(os.path.exists(cover_picture_path))


@pytest.mark.django_db
class TestMyWallView(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.cricketer = CricketerFactory()
        self.user = self.cricketer.user

        self.friend1 = CricketerFactory().user
        self.friend2 = CricketerFactory().user
        self.friend3 = CricketerFactory().user
        self.friend4 = CricketerFactory().user
        self.user.add_friend(self.friend1)
        self.user.add_friend(self.friend2)
        self.user.add_friend(self.friend3)
        self.user.add_friend(self.friend4)

        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('my_wall')
        self.response = self.client.get(self.url)

    def test_returns_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_returns_correct_context_parameters(self):
        self.assertIn('user_wall_posts', self.response.context_data)

    def test_returns_self_user_wall_posts(self):
        user_wall_post1 = UserWallPostFactory(cricketer=self.cricketer)
        user_wall_post2 = UserWallPostFactory(cricketer=self.cricketer)
        user_wall_post3 = UserWallPostFactory(cricketer=self.cricketer)
        response = self.client.get(self.url)
        user_wall_posts = list(response.context_data['user_wall_posts'])
        self.assertEqual(len(user_wall_posts), 3)
        self.assertEqual(user_wall_posts, [user_wall_post3, user_wall_post2, user_wall_post1])

    def test_returns_friends_user_wall_posts_in_context_also(self):
        non_friend_user = CricketerFactory().user
        user_wall_post1 = UserWallPostFactory(cricketer=self.cricketer)
        user_wall_post2 = UserWallPostFactory(cricketer=self.friend1.cricketer)
        user_wall_post3 = UserWallPostFactory(cricketer=self.friend2.cricketer)
        user_wall_post4 = UserWallPostFactory(cricketer=non_friend_user.cricketer)
        response = self.client.get(self.url)
        user_wall_posts = list(response.context_data['user_wall_posts'])
        self.assertEqual(len(user_wall_posts), 3)
        self.assertEqual(user_wall_posts, [user_wall_post3, user_wall_post2, user_wall_post1])

    def test_returns_latest_messages_as_global_context_parameter(self):
        self.assertIn('latest_received_messages', self.response.context)

    def test_returns_friends_as_global_context_parameter(self):
        self.assertIn('friends', self.response.context)

    def test_returns_friend_count_as_global_context_parameter(self):
        self.assertIn('friends_count', self.response.context)

    def test_returns_friend_suggestions_as_global_context_parameter(self):
        self.assertIn('friend_suggestions', self.response.context)

    def test_returns_team_follow_suggestions_as_global_context_parameter(self):
        self.assertIn('team_follow_suggestions', self.response.context)

    def test_returns_latest_requests_as_global_context_parameter(self):
        self.assertIn('latest_friend_requests', self.response.context)

    def test_returns_messages_count_as_global_context_parameter(self):
        self.assertIn('messages_notification_count', self.response.context)

    def test_returns_friend_requests_count_as_global_context_parameter(self):
        self.assertIn('friend_requests_notification_count', self.response.context)

    def test_returns_latest_user_notifications_as_global_context_parameter(self):
        self.assertIn('latest_user_notifications', self.response.context)

    def test_returns_user_notifications_count_as_global_context_parameter(self):
        self.assertIn('user_notifications_count', self.response.context)

    def test_correct_template_used(self):
        self.assertIn('accounts/my_wall.html', self.response.template_name)

    def test_returns_friend_requests_count(self):
        friend_request1 = FriendRequestFactory(from_user=self.friend1, to_user=self.user)
        friend_request2 = FriendRequestFactory(from_user=self.friend2, to_user=self.user)
        friend_request3 = FriendRequestFactory(from_user=self.friend3, to_user=self.user)
        friend_request4 = FriendRequestFactory(from_user=self.friend4, to_user=self.user)
        response = self.client.get(self.url)
        self.assertIn('friend_requests_notification_count', response.context)
        self.assertEqual(response.context['friend_requests_notification_count'], 4)

    def test_returns_friend_requests_count_excluding_viewed_requests(self):
        friend_request1 = FriendRequestFactory(from_user=self.friend1, to_user=self.user, viewed=True)
        friend_request2 = FriendRequestFactory(from_user=self.friend2, to_user=self.user, viewed=True)
        friend_request3 = FriendRequestFactory(from_user=self.friend3, to_user=self.user)
        friend_request4 = FriendRequestFactory(from_user=self.friend4, to_user=self.user)
        response = self.client.get(self.url)
        self.assertIn('friend_requests_notification_count', response.context)
        self.assertEqual(response.context['friend_requests_notification_count'], 2)

    def test_returns_messages_count(self):
        message1 = MessageFactory(sender=self.friend1, recipient=self.user)
        message2 = MessageFactory(sender=self.friend1, recipient=self.user)
        message3 = MessageFactory(sender=self.friend2, recipient=self.user)
        message4 = MessageFactory(sender=self.friend2, recipient=self.user)
        message5 = MessageFactory(sender=self.friend3, recipient=self.user)
        message6 = MessageFactory(sender=self.friend3, recipient=self.user)
        message7 = MessageFactory(sender=self.friend4, recipient=self.user)
        message8 = MessageFactory(sender=self.friend4, recipient=self.user)
        response = self.client.get(self.url)
        self.assertIn('messages_notification_count', response.context)
        self.assertEqual(response.context['messages_notification_count'], 4)

    def test_returns_messages_count_excluding_read_messages(self):
        message1 = MessageFactory(sender=self.friend1, recipient=self.user, unread=False)
        message2 = MessageFactory(sender=self.friend1, recipient=self.user, unread=False)
        message3 = MessageFactory(sender=self.friend2, recipient=self.user, unread=False)
        message4 = MessageFactory(sender=self.friend2, recipient=self.user)
        message5 = MessageFactory(sender=self.friend3, recipient=self.user)
        message6 = MessageFactory(sender=self.friend3, recipient=self.user)
        message7 = MessageFactory(sender=self.friend4, recipient=self.user)
        message8 = MessageFactory(sender=self.friend4, recipient=self.user)
        response = self.client.get(self.url)
        self.assertIn('messages_notification_count', response.context)
        self.assertEqual(response.context['messages_notification_count'], 3)

    def test_returns_messages_count_excluding_deleted_by_recipient_messages(self):
        message1 = MessageFactory(sender=self.friend1, recipient=self.user, deleted_by_recipient=True)
        message2 = MessageFactory(sender=self.friend1, recipient=self.user, deleted_by_recipient=True)
        message3 = MessageFactory(sender=self.friend2, recipient=self.user, deleted_by_recipient=True)
        message4 = MessageFactory(sender=self.friend2, recipient=self.user)
        message5 = MessageFactory(sender=self.friend3, recipient=self.user)
        message6 = MessageFactory(sender=self.friend3, recipient=self.user)
        message7 = MessageFactory(sender=self.friend4, recipient=self.user)
        message8 = MessageFactory(sender=self.friend4, recipient=self.user)
        response = self.client.get(self.url)
        self.assertIn('messages_notification_count', response.context)
        self.assertEqual(response.context['messages_notification_count'], 3)

    def test_returns_notifications_count(self):
        notification1 = FriendRequestAcceptNotificationFactory(user=self.user)
        notification2 = FriendRequestAcceptNotificationFactory(user=self.user)
        notification3 = FriendRequestAcceptNotificationFactory(user=self.user)
        notification4 = FriendRequestAcceptNotificationFactory(user=self.user)
        response = self.client.get(self.url)
        self.assertIn('user_notifications_count', response.context)
        self.assertEqual(response.context['user_notifications_count'], 4)

    def test_returns_notifications_count_excluding_viewed(self):
        notification1 = FriendRequestAcceptNotificationFactory(user=self.user, viewed=True)
        notification2 = FriendRequestAcceptNotificationFactory(user=self.user)
        notification3 = FriendRequestAcceptNotificationFactory(user=self.user, viewed=True)
        notification4 = FriendRequestAcceptNotificationFactory(user=self.user)
        response = self.client.get(self.url)
        self.assertIn('user_notifications_count', response.context)
        self.assertEqual(response.context['user_notifications_count'], 2)

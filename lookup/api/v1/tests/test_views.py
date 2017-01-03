# inbuilt python imports
import unittest
import json

# inbuilt django imports
from django.test import Client

# third-party django imports

# inter-app imports

# local imports
from lookup.choices import COUNTRY_CHOICES, COUNTRY_CODE_MAPPING, STATE_CHOICES, STATE_TO_CITY_CHOICES


class TestCountryLookup(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.url = '/api/v1/lookup/country/'
        self.response = self.client.get(self.url)

    def test_returns_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_returns_countries_choices(self):
        self.assertEqual(self.response.data, COUNTRY_CHOICES)


class TestCountryToCountryCodeLookup(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.url = '/api/v1/lookup/country-code/?country=IN'
        self.response = self.client.get(self.url)

    def test_returns_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_returns_country_code(self):
        self.assertEqual(self.response.data['country_code'], '91')

    def test_returns_error_if_country_missing(self):
        url = '/api/v1/lookup/country-code/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['country_code'], 'Invalid value for country.')

    def test_returns_error_if_country_invalid(self):
        url = '/api/v1/lookup/country-code/?country=AAAAA'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['country_code'], 'Invalid value for country.')


class TestStateLookup(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.url = '/api/v1/lookup/state/'
        self.response = self.client.get(self.url)

    def test_returns_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_returns_countries_choices(self):
        self.assertEqual(self.response.data, STATE_CHOICES)


class TestStateToCityLookup(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.state = 1012
        self.url = '/api/v1/lookup/city/?state={}'.format(self.state)
        self.response = self.client.get(self.url)

    def test_returns_200_response(self):
        self.assertEqual(self.response.status_code, 200)

    def test_returns_country_code(self):
        self.assertEqual(self.response.data['city'], STATE_TO_CITY_CHOICES[self.state])

    def test_returns_error_if_country_missing(self):
        url = '/api/v1/lookup/city/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['city'], 'Invalid value for state.')

    def test_returns_error_if_country_invalid(self):
        url = '/api/v1/lookup/city/?state=99999999'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['city'], 'Invalid value for state.')

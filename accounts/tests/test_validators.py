# inbuilt python imports
import unittest

# inbuilt django imports
from django.test import Client
from django.core.exceptions import ValidationError

# third-party django imports
import pytest

# inter-app imports

# local imports
from ..validators import validate_full_name


class TestFullNameValidator(unittest.TestCase):

    def setUp(self):
        self.Client = Client()
        self.name = 'jon snow'

    def test_validates_name(self):
        try:
            validate_full_name(self.name)
        except ValidationError:
            self.fail('validate_full_name() raised ValidationError unexpectedly!')

    def test_raises_exception_on_only_first_name(self):
        self.name = 'jon'
        self.assertRaises(ValidationError, validate_full_name, self.name)

    def test_raises_exception_on_only_first_name_with_spaces(self):
        self.name = '   jon  '
        self.assertRaises(ValidationError, validate_full_name, self.name)

    def test_name_valid_if_single_word_with_dot(self):
        self.name = ' s.kartik '
        try:
            validate_full_name(self.name)
        except ValidationError:
            self.fail('validate_full_name() raised ValidationError unexpectedly!')

    def test_name_valid_with_space_and_dot(self):
        self.name = ' s. kartik '
        try:
            validate_full_name(self.name)
        except ValidationError:
            self.fail('validate_full_name() raised ValidationError unexpectedly!')


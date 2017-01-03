# Python Imports

# Django Imports
from django.core.exceptions import ValidationError

# Third Party Django Imports

# Inter App Imports

# Local Imports


def validate_full_name(value):
    value = value.strip()
    name_parts = value.split()
    dot_parts = value.split('.')
    if len(name_parts) < 2 and len(dot_parts) < 2:
        raise ValidationError('Please enter full name.')

# Python Imports
import random

# Django Imports
from django import template

# Third Party Django Imports

# Inter App Imports

# Local Imports

register = template.Library()


@register.filter
def shuffle(arg):
    tmp = list(arg)[:]
    random.shuffle(tmp)
    return tmp

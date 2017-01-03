# Python Imports

# Django Imports
from django.template.defaultfilters import slugify

# Third Party Django Imports

# Inter App Imports

# Local Imports


def prepare_name_and_id_slug(name, object_id):
    slug_string = '{} {}'.format(name, object_id)
    slug = slugify(slug_string)
    return slug

# Python Imports

# Django Imports

# Third Party Django Imports
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination

# Inter App Imports

# Local Imports


class PostLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 10


class PostPageNumberPagination(PageNumberPagination):
    page_size = 10

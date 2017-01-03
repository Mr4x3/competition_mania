# Python Imports

# Django Imports

# Third Party Django Imports
from rest_framework import mixins
from rest_framework import viewsets

# Inter App Imports

# Local Imports


class CreateDestroyViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    """
    A Viewset That Provides `Create`, And `Destroy` Actions.

    To Use It, Override the Class And Set the `.Queryset` And
    `.Serializer_class` Attributes.
    """
    pass

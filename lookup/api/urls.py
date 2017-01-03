# Python Imports

# Django Imports
from django.conf.urls import url, include

# Third Party Django Imports

# Inter App Imports

# Local Imports


urlpatterns = [
    url(r'^v1/lookup/', include('lookup.api.v1.urls')),
]

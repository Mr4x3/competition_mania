# Python Imports

# Django Imports
from django.conf.urls import url, include

# Third Party Django Imports

# Inter App Imports

# Local Imports

urlpatterns = [
    url(r'^api/', include('lookup.api.urls')),
]

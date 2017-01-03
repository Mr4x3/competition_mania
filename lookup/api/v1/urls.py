# Python Imports

# Django Imports
from django.conf.urls import url

# Third Party Django Imports

# Inter App Imports

# Local Imports
from .views import CountryLookup, CountryToCountryCodeLookup, StateLookup, StateToCityLookup


urlpatterns = [
    url(r'^country/$', CountryLookup.as_view()),
    url(r'^country-code/$', CountryToCountryCodeLookup.as_view()),
    url(r'^state/$', StateLookup.as_view()),
    url(r'^city/$', StateToCityLookup.as_view()),
]

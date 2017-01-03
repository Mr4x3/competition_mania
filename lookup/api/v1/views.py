# Python Imports

# Django Imports

# Third Party Django Imports
from rest_framework.views import APIView
from rest_framework.response import Response

# Inter App Imports
from lookup.choices import COUNTRY_CHOICES, COUNTRY_CODE_MAPPING, STATE_CHOICES, STATE_TO_CITY_CHOICES

# Local Imports


class CountryLookup(APIView):
    """
    Returns Countries Lookup
    """

    def get(self, request):
        return Response(data=COUNTRY_CHOICES, content_type='application/json')


class CountryToCountryCodeLookup(APIView):
    """
    Returns Country Code Based On Country Selected
    """

    def get(self, request):
        country = request.query_params.get('country')

        if country not in COUNTRY_CODE_MAPPING:
            return Response(data={'country_code': 'Invalid value for country.'}, content_type='application/json', status=400)

        return Response(data={'country_code': COUNTRY_CODE_MAPPING[country]}, content_type='application/json')


class StateLookup(APIView):
    """
    Returns Indian States Lookup
    """

    def get(self, request):
        return Response(data=STATE_CHOICES, content_type='application/json')


class StateToCityLookup(APIView):
    """
    Returns Country Code Based On Country Selected
    """

    def get(self, request):
        state = request.query_params.get('state', '')

        if not state.isdigit() or int(state) not in STATE_TO_CITY_CHOICES:
            return Response(data={'city': 'Invalid value for state.'}, content_type='application/json', status=400)

        return Response(data={'city': STATE_TO_CITY_CHOICES[int(state)]}, content_type='application/json')

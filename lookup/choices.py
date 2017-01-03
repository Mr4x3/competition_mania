# Python Imports
from functools import reduce

# Django Imports

# Third Party Django Imports

# Inter App Imports

# Local Imports
from .static_lookups import COUNTRY_CODE_MAPPING, STATE_TO_CITY_CHOICES, COUNTRY_CHOICES, STATE_CHOICES


GENDER_CHOICES = [('M', 'Male'), ('F', 'Female')]

SPORTS_CHOICES = [
    ('cricket', 'Cricket'),
]

COUNTRY_CODE_CHOICES = [(x, x) for x in COUNTRY_CODE_MAPPING.values()]

CITY_CHOICES = reduce(lambda x, y: x+y, STATE_TO_CITY_CHOICES.values())  # Prepare List of Tuples
CITY_CHOICES = sorted(CITY_CHOICES, key=lambda x: x[0])  # Sort Them Via City_id

CITY_CHOICES_ALPHABETIC = sorted(CITY_CHOICES, key=lambda x: x[1])  # Sorted By Alphabet

NUMBER_OF_VACANCY = [
    (1, '01'),
    (2, '02'),
    (3, '03'),
    (4, '04'),
    (5, '05'),
    (6, '06'),
    (7, '07'),
    (8, '08'),
    (9, '09'),
    (10, '10'),
]


REGISTRATION_SOURCE_CHOICES = [
    (1, 'normal'),
    (2, 'facebook'),
    (3, 'google'),
    (4, 'twitter')
]

REGISTRATION_SOURCE_MAPPING = {v: k for k, v in REGISTRATION_SOURCE_CHOICES}

USER_WALL_POST_TYPE_CHOICES = [
    (1, 'text'),
    (2, 'image'),
    (3, 'location')
]

STATE_TO_CITY_IDS = {}
for state, cities in STATE_TO_CITY_CHOICES.items():
    STATE_TO_CITY_IDS[state] = [city[0] for city in cities]

USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING = {
    1: 'You and <b>{friend}</b> are now friends.',
    2: 'You have been added as a member of {cricket_team}',
    3: 'You have been chosen as the Captain of {cricket_team}.',
    4: 'You have been chosen as the Vice Captain of {cricket_team}.',
    5: 'You have been added to the playing eleven of {cricket_team}.',
    6: 'Score Sheet updated for {cricket_team}.',
    7: 'You have been chosen as the Man Of The Match of {cricket_team}',
    8: 'You have been chosen as the Best Batsman of {cricket_team}.',
    9: 'You have been chosen as the Best Bowler of {cricket_team}.',
    10: 'You have been chosen as the Best Fielder of {cricket_team}.',
    11: '{user_name} is now following {cricket_team}.',
    12: '{from_user} invited you to join {cricket_team}',
    13: '{friend} has commented on Your Post',
    14: '{friend} has Liked Your Post',
    15: '{cricket_team} is looking for Players for their Team',
}

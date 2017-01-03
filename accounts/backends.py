# Python Imports

# Django Imports
from django.contrib.auth import get_user_model

# Third Party Django Imports

# Inter App Imports

# Local Imports


class EmailAuthenticationBackend(object):
    """
    This Authentication Backend Authenticates a User Against an Email.
    """

    def authenticate(self, username=None, password=None):
        """
        Authenticate Using the Email/password And Return a User
        """

        UserModel = get_user_model()
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        """
        Returns a User Against a Given User Id
        """

        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None


class MobileAuthenticationBackend(object):
    """
    This Authentication Backend Authenticates a User Against the Mobile No.
    Possible Usage Can Be Facebook Login Where User Can Also Use Mobile No. to
    Create an Account.
    """

    def authenticate(self, username=None, password=None):
        """
        Authenticate Using the Mobile/password And Return a User
        """

        UserModel = get_user_model()
        try:
            user = UserModel._default_manager.get(mobile=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        """
        Returns a User Against a Given User Id
        """

        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None


class SocialProfileIdAuthenticationBackend(object):
    """
    This Authentication Backend Authenticates a User Against the Social Id
    """

    def authenticate(self, username=None, password=None):
        """
        Authenticate Using the Mobile/password And Return a User
        """

        UserModel = get_user_model()
        try:
            user = UserModel._default_manager.get(social_profile_id=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        """
        Returns a User Against a Given User Id
        """

        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None

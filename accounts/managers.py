# Python Imports

# Django Imports
from django.contrib.auth.models import BaseUserManager

# Third Party Django Imports

# Inter App Imports

# Local Imports


class UserManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        """
        Creates And Saves a User with the Given Email, First Name, Last Name
        And Password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(email=self.normalize_email(email), first_name=first_name, last_name=last_name, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password, **extra_fields):
        """
        Creates And Saves a Superuser with the Given Email, First Name, Last Name
        And Password.
        """
        user = self.create_user(email, password=password, first_name=first_name, last_name=last_name, **extra_fields)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

# Python Imports

# Django Imports
from django import forms
from django.contrib.auth import authenticate
from django.contrib.admin.widgets import AdminDateWidget

# Third Party Django Imports

# Inter App Imports
from lookup.choices import REGISTRATION_SOURCE_MAPPING, STATE_TO_CITY_IDS

# Local Imports
from .models import User
from .validators import validate_full_name
from .utils import get_first_and_last_name


class LoginForm(forms.Form):
    """
    Login Form
    """

    email = forms.EmailField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Email ID'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('This email is not registered with us.')
        return email

    def clean(self):
        # import ipdb; ipdb.set_trace()
        cleaned_data = super(LoginForm, self).clean()
        if not self._errors:
            self.user = authenticate(username=cleaned_data['email'], password=cleaned_data['password'])
            if not self.user:
                self._errors['email'] = self.error_class(['EMAIL ID and Password do not match'])
        return cleaned_data

    def get_authenticated_user(self):
        return getattr(self, 'user', None)


class UserRegistrationForm(forms.ModelForm):
    """
    User Registration Form
    """

    first_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))

    class Meta:
        model = User
        fields = ['email']
        widgets = {
            'email': forms.TextInput(attrs={'placeholder': 'Email ID'}),
        }

    def clean_email(self):
        # import ipdb; ipdb.set_trace()
        if User.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError('Email id already exists')
        return self.cleaned_data.get('email', '').lower()

    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.first_name = self.cleaned_data.get('first_name', None)
        user.last_name = self.cleaned_data.get('last_name', None)
        user.set_password('IGotThePower')
        if commit:
            user.save()
        return user


class UserProfileFormMixin(forms.ModelForm):

    name = forms.CharField(validators=[validate_full_name])

    class Meta:
        model = User
        fields = ['email', 'gender', 'display_picture', 'cover_picture', 'country', 'date_of_birth', 'mobile', 'city', 'city_text', 'state', 'state_text']
        widgets = {
            'state_text': forms.TextInput(attrs={'placeholder': 'Please enter your state'}),
            'city_text': forms.TextInput(attrs={'placeholder': 'Please enter your city'}),
            'mobile': forms.TextInput(attrs={'placeholder': 'Enter mobile no'}),
            'gender': forms.RadioSelect()
        }

    def clean_name(self):
        self.first_name, self.last_name = get_first_and_last_name(self.cleaned_data['name'])
        if not self.first_name or not self.last_name:
            raise forms.ValidationError('Please enter full name.')
        return self.cleaned_data['name']

    def clean_state_value(self):
        if self.cleaned_data.get('country') == 'IN':
            if not self.cleaned_data.get('state'):
                self._errors['state'] = self.error_class(["Please choose a value for state"])
        elif not self.cleaned_data.get('state_text'):
            self._errors['state_text'] = self.error_class(["Please enter a value for state"])

    def clean_city_value(self):
        if self.cleaned_data.get('country') == 'IN':
            if not self.cleaned_data.get('city'):
                self._errors['city'] = self.error_class(["Please choose a value for city"])
            if self.cleaned_data['city'] and self.cleaned_data['city'] not in STATE_TO_CITY_IDS[self.cleaned_data['state']]:
                self._errors['city'] = self.error_class(["Please choose a correct city value"])
        elif not self.cleaned_data.get('city_text'):
            self._errors['city_text'] = self.error_class(["Please enter a value for city"])

    def clean(self):
        self.cleaned_data = super(UserProfileFormMixin, self).clean()
        if not self._errors:
            self.clean_state_value()
        if not self._errors:
            self.clean_city_value()
        return self.cleaned_data

    def save(self, commit=True):
        user = super(UserProfileFormMixin, self).save(commit=False)
        user.first_name = self.first_name
        user.last_name = self.last_name
        user.registration_midout = False
        if commit:
            user.save()
        return user


class ProfileSpecificRegistrationForm(UserProfileFormMixin):

    def clean_email(self):
        if self.cleaned_data['email'].lower() != self.instance.email.lower() and self.instance.registration_source != REGISTRATION_SOURCE_MAPPING['facebook']:
            raise forms.ValidationError('Email cannot be edited')
        return self.cleaned_data['email'].lower()


class EditUserProfileForm(UserProfileFormMixin):

    def __init__(self, *args, **kwargs):
        super(EditUserProfileForm, self).__init__(*args, **kwargs)
        custom_template_with_initial = '%(clear_template)s<br />%(input_text)s: %(input)s'
        display_picture_widget = self.fields['display_picture'].widget
        cover_picture_widget = self.fields['cover_picture'].widget
        display_picture_widget.template_with_initial = custom_template_with_initial
        cover_picture_widget.template_with_initial = custom_template_with_initial

    def clean_email(self):
        if self.cleaned_data['email'].lower() != self.instance.email.lower():
            raise forms.ValidationError('Email cannot be edited')
        return self.cleaned_data['email'].lower()


class ChangePasswordForm(forms.Form):

    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'New Password'}), min_length=6)
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

    def clean(self):
        """
        Verifies That the Values Entered Into the Password Fields Match
        """
        cleaned_data = super(ChangePasswordForm, self).clean()
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                self._errors['password1'] = self.error_class("Passwords do not match.")
        return self.cleaned_data


class LoginAsUserForm(forms.Form):
    """
    Login As Another User
    """
    username = forms.EmailField(widget=forms.TextInput(attrs={'placeholder': 'Email Id'}))

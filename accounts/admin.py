# # Python Imports

# # Django Imports
# from django.contrib import admin
# from django.contrib.auth.models import Group
# from django import forms

# # Third Party Django Imports
# from import_export import resources
# from import_export.admin import ImportExportActionModelAdmin

# # Inter App Imports
# from lookup.choices import STATE_TO_CITY_IDS

# # Local Imports
# from .models import User


# class UserAdminForm(forms.ModelForm):
#     class Meta:
#         model = User
#         exclude = ('password', 'social_profile_id', 'friends')

#     def __init__(self, *args, **kwargs):

#         super(UserAdminForm, self).__init__(*args, **kwargs)
#         if not self.instance or not self.instance.id:
#             self.fields['registration_midout'].initial = False

#     def clean_state_value(self):
#         if self.cleaned_data.get('country') == 'IN':
#             if not self.cleaned_data.get('state'):
#                 self._errors['state'] = self.error_class(["Please choose a value for state"])
#         elif not self.cleaned_data.get('state_text'):
#             self._errors['state_text'] = self.error_class(["Please enter a value for state"])

#     def clean_city_value(self):
#         if self.cleaned_data.get('country') == 'IN':
#             if not self.cleaned_data.get('city'):
#                 self._errors['city'] = self.error_class(["Please choose a value for city"])
#             if self.cleaned_data['city'] and self.cleaned_data['city'] not in STATE_TO_CITY_IDS[self.cleaned_data['state']]:
#                 self._errors['city'] = self.error_class(["Please choose a correct city value"])
#         elif not self.cleaned_data.get('city_text'):
#             self._errors['city_text'] = self.error_class(["Please enter a value for city"])

#     def clean(self):
#         self.cleaned_data = super(UserAdminForm, self).clean()
#         if not self._errors:
#             self.clean_state_value()
#         if not self._errors:
#             self.clean_city_value()
#         return self.cleaned_data


# class UserResource(resources.ModelResource):
#     class Meta:
#         model = User
#         exclude = ('password', 'social_profile_id', 'friends')


# class UserAdmin(ImportExportActionModelAdmin):
#     resource_class = UserResource
#     form = UserAdminForm
#     readonly_fields = ('slug',)
#     list_display = ('first_name', 'last_name', 'email')
#     list_display_links = ('first_name', 'email')
#     list_filter = ['created_on']
#     search_fields = ('first_name', 'last_name', 'email')

# admin.site.unregister(Group)
# admin.site.register(User, UserAdmin)

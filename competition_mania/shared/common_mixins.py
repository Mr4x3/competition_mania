# Python Imports
import base64
import uuid
import re

# Django Imports
from django.views.decorators.csrf import csrf_exempt
from django.utils.http import urlquote
from django.shortcuts import redirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.conf import settings
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from django.core.files.uploadedfile import SimpleUploadedFile

# Third Party Django Imports

# Inter App Imports
from accounts.models import User
# from cricket.models import CricketTeam, CricketMatch, CricketTeamMember, TeamMemberVacancy
from accounts.utils import decode_token

# Local Imports


# class CsrfExemptMixin(object):

#     @csrf_exempt
#     def dispatch(self, *args,  **kwargs):
#         return super(CsrfExemptMixin, self).dispatch(*args, **kwargs)


# class LoginRequiredMixin(object):
#     """
#     This Checks If the User Is Logged-in Or Not
#     """

#     def get_url_to_redirect(self, request, url):
#         return url + "?next=" + urlquote(request.get_full_path())

#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_authenticated():
#             return redirect(self.get_url_to_redirect(request, settings.LOGIN_URL))

#         return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)


class CheckLoggedInMixin(object):
    """
    This Redirects to Mywall If the User Is Logged-in
    """

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse('my_wall'))

        return super(CheckLoggedInMixin, self).dispatch(request, *args, **kwargs)


# class CommonMethodsMixin(object):

#     def get_redirect_url(self, request, url):
#         """
#         This Returns a Url with the Original Request Query Parameters Intact.
#         """
#         query_string = request.META.get('QUERY_STRING')
#         if query_string:
#             url += '?' + query_string
#         return url


class TokenAutoLoginMixin(object):
    """
    Validates the Token in the Url And Autologin the User.
    """

    def dispatch(self, request, *args, **kwargs):
        token = self.kwargs['token']
        user, token_type, token_expired = decode_token(token)

        if not user or token_expired:
            return HttpResponseRedirect(reverse_lazy('change_password'))

        # perform login
        user.backend = 'accounts.backends.EmailAuthenticationBackend'
        login(request, user)

        return super(TokenAutoLoginMixin, self).dispatch(request, *args, **kwargs)


# class EmailNotVerifiedMixin(CommonMethodsMixin):
#     """
#     This Checks If the Email Has Been Verified Or Not.
#     """

#     def dispatch(self, request, *args, **kwargs):
#         if request.user.is_email_verified:
#             return redirect(self.get_redirect_url(request, reverse('cricket_profile_registration')))

#         return super(EmailNotVerifiedMixin, self).dispatch(request, *args, **kwargs)


# class EmailVerifiedMixin(CommonMethodsMixin):
#     """
#     This Checks If the Email Has Been Verified Or Not.
#     """

#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_email_verified:
#             return redirect(self.get_redirect_url(request, reverse('verify_email')))

#         return super(EmailVerifiedMixin, self).dispatch(request, *args, **kwargs)


# class UserProfileMidoutRequiredMixin(CommonMethodsMixin):
#     """
#     This Checks If the User Has Completed Homepage (1st Page) Registration Or Not.
#     """

#     def dispatch(self, request, *args, **kwargs):
#         if request.user.has_sports_profile():

#             if not request.user.is_registration_midout():
#                 return redirect(self.get_redirect_url(request, reverse('my_wall')))

#             return redirect(self.get_redirect_url(request, reverse('profile_specific_registration')))

#         return super(UserProfileMidoutRequiredMixin, self).dispatch(request, *args, **kwargs)


# class UserProfileRequiredMixin(CommonMethodsMixin):
#     """
#     This Checks If the User Is Has Completed Profile Specific (2nd Page) Registration Or Not.
#     """

#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_registration_midout():
#             return redirect(self.get_redirect_url(request, reverse('my_wall')))

#         if not request.user.has_sports_profile():
#             return redirect(self.get_redirect_url(request, reverse('cricket_profile_registration')))

#         return super(UserProfileRequiredMixin, self).dispatch(request, *args, **kwargs)


# class SportsProfileRequiredMixin(CommonMethodsMixin):
#     """
#     This Checks If the User Is Has Completed Sports Specific (3rd Page) Registration Or Not.
#     """

#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_anonymous():
#             if request.user.is_registration_midout():
#                 return redirect(self.get_redirect_url(request, reverse('profile_specific_registration')))

#             if not request.user.has_sports_profile():
#                 return redirect(self.get_redirect_url(request, reverse('cricket_profile_registration')))

#         return super(SportsProfileRequiredMixin, self).dispatch(request, *args, **kwargs)


# class TeamMidoutRequiredMixin(CommonMethodsMixin):

#     def dispatch(self, request, *args, **kwargs):
#         team_slug = self.kwargs['slug']
#         try:
#             self.team = CricketTeam.objects.get(slug=team_slug, is_deleted=False)
#         except CricketTeam.DoesNotExist:
#             return redirect(self.get_redirect_url(request, reverse('cricket_team_registration')))

#         if not self.team.registration_midout:
#             return redirect(self.get_redirect_url(request, reverse('cricket_team_wall', kwargs={'slug':self.team.slug})))

#         if self.team.super_admin.user != self.request.user:  # Only Super Admin Can Add Team Members
#             return redirect(self.get_redirect_url(request, reverse('cricket_team_registration')))

#         return super(TeamMidoutRequiredMixin, self).dispatch(request, *args, **kwargs)


# class TeamWallNotVisitedMixin(CommonMethodsMixin):

#     def dispatch(self, request, *args, **kwargs):
#         team_slug = self.kwargs['slug']
#         try:
#             self.team = CricketTeam.objects.get(slug=team_slug, is_deleted=False)
#         except CricketTeam.DoesNotExist:
#             return redirect(self.get_redirect_url(request, reverse('cricket_team_registration')))

#         if self.team.has_wall_visited:
#             return redirect(self.get_redirect_url(request, reverse('cricket_team_wall', kwargs={'slug':self.team.slug})))

#         return super(TeamWallNotVisitedMixin, self).dispatch(request, *args, **kwargs)


# class TeamRequiredMixin(CommonMethodsMixin):

#     def dispatch(self, request, *args, **kwargs):
#         team_slug = self.kwargs['slug']
#         try:
#             self.team = CricketTeam.objects.get(slug=team_slug, is_deleted=False)
#         except CricketTeam.DoesNotExist:
#             return redirect(self.get_redirect_url(request, reverse('cricket_team_registration')))

#         # if self.team.registration_midout:
#         #     return redirect(self.get_redirect_url(request, reverse('cricket_team_members_registration', kwargs={'slug':self.team.slug})))

#         return super(TeamRequiredMixin, self).dispatch(request, *args, **kwargs)


# class CricketMatchMidoutRequiredMixin(CommonMethodsMixin):

#     def dispatch(self, request, *args, **kwargs):

#         match_id = self.kwargs['match_id']
#         try:
#             self.team_match = CricketMatch.objects.get(id=match_id)
#         except CricketMatch.DoesNotExist:
#             return redirect(self.get_redirect_url(request, reverse('create_cricket_match_playing_eleven', kwargs={'slug':self.team.slug})))

#         if not self.team_match.registration_midout:
#             return redirect(self.get_redirect_url(request, reverse('cricket_team_wall', kwargs={'slug':self.team.slug})))

#         return super(CricketMatchMidoutRequiredMixin, self).dispatch(request, *args, **kwargs)


# class CricketMatchRequiredMixin(CommonMethodsMixin):

#     def dispatch(self, request, *args, **kwargs):

#         match_id = self.kwargs['match_id']
#         try:
#             self.team_match = CricketMatch.objects.get(id=match_id)
#         except CricketMatch.DoesNotExist:
#             return redirect(self.get_redirect_url(request, reverse('create_cricket_match_playing_eleven', kwargs={'slug':self.team.slug})))

#         # if self.team_match.registration_midout:
#         #     return redirect(self.get_redirect_url(request, reverse('create_cricket_match_score_sheet', kwargs={'slug':self.team.slug, 'match_id':match_id})))

#         return super(CricketMatchRequiredMixin, self).dispatch(request, *args, **kwargs)


# class CricketTeamWritePermissionsMixin(CommonMethodsMixin):

#     def dispatch(self, request, *args, **kwargs):
#         # Check User Has Write Permissions
#         self.team_member = CricketTeamMember.objects.filter(team=self.team, cricketer=request.user.cricketer, is_active=True).first()
#         if not self.team_member or not self.team_member.has_write_permissions():
#             return redirect(self.get_redirect_url(request, reverse('cricket_team_wall', kwargs={'slug':self.team.slug})))

#         return super(CricketTeamWritePermissionsMixin, self).dispatch(request, *args, **kwargs)


# class CricketTeamWritePermissionsNSuperUserMixin(CommonMethodsMixin):

#     def dispatch(self, request, *args, **kwargs):
#         # Check User Has Write Permissions
#         if request.user.is_staff:
#             return super(CricketTeamWritePermissionsNSuperUserMixin, self).dispatch(request, *args, **kwargs)
#         else:
#             self.team_member = CricketTeamMember.objects.filter(team=self.team, cricketer=request.user.cricketer, is_active=True).first()
#             if not self.team_member or not self.team_member.has_write_permissions():
#                 return redirect(self.get_redirect_url(request, reverse('cricket_team_wall', kwargs={'slug':self.team.slug})))

#         return super(CricketTeamWritePermissionsNSuperUserMixin, self).dispatch(request, *args, **kwargs)


# class CompleteCricketerRequiredMixin(CommonMethodsMixin):

#     def dispatch(self, request, *args, **kwargs):
#         clicked_user_slug = self.kwargs['slug']
#         try:
#             self.viewed_user = User.objects.get(slug=clicked_user_slug)
#         except User.DoesNotExist:
#             if not self.request.user.is_anonymous():
#                 return redirect(self.get_redirect_url(request, reverse('my_wall')))

#         if not self.viewed_user.is_email_verified or self.viewed_user.is_registration_midout() or not self.viewed_user.has_sports_profile():
#             return redirect(self.get_redirect_url(request, reverse('my_wall')))

#         return super(CompleteCricketerRequiredMixin, self).dispatch(request, *args, **kwargs)


# class ImageCropperMixin(object):
#     """
#     This Takes Base64 Encoded Cropped Image String And Decodes This String to Generate
#     Image File Object. This Image Object Is Then Injected Into the Files Data Instead of the
#     String.
#     """

#     ENCODED_STRING_REGEX = r'^data:(?P<image_format>\w+/\w+);base64,(?P<image_string>.*)$'

#     def get_image_file_from_base64_string(self, image_field):

#         image_format, image_base64_string = re.search(self.ENCODED_STRING_REGEX, self.request.POST[image_field]).groups()
#         image_name = '{}.{}'.format(str(uuid.uuid4()), image_format.split('/')[1])
#         image_content = base64.urlsafe_b64decode(bytes(image_base64_string, 'utf-8'))
#         image_file = SimpleUploadedFile(name=image_name, content=image_content, content_type=image_format)
#         return image_file

#     def dispatch(self, request, *args, **kwargs):

#         request.POST._mutable = True
#         # Replace Base64 Image String with Image File in Request
#         for image_field in self.image_fields:
#             if request.POST.get(image_field):
#                 image_file = self.get_image_file_from_base64_string(image_field)
#                 request.FILES[image_field] = image_file  # Add File to Files Dictionary
#                 request.POST.pop(image_field, None)  # Remove Key From Post Dictionary

#         request.POST._mutable = False

#         return super(ImageCropperMixin, self).dispatch(request, *args, **kwargs)


# class SuperUserRequiredMixin(object):
#     """
#     View Mixin Which Requires That the Authenticated User Is a Super User (i.e. "is_superuser" Is True).
#     """

#     def dispatch(self, request, *args, **kwargs):
#         if not request.user.is_superuser:
#             return redirect(reverse_lazy('homepage'))
#         return super(SuperUserRequiredMixin, self).dispatch(request, *args, **kwargs)


# class TeamMemberVacancyRequestMixin(CommonMethodsMixin):
#     """
#     Dont Let In If Vacancy Request Already made
#     """
#     def dispatch(self, request, *args, **kwargs):
#         team_slug = self.kwargs['slug']
#         try:
#             self.team = CricketTeam.objects.get(slug=team_slug, is_deleted=False)
#         except CricketTeam.DoesNotExist:
#             return redirect(self.get_redirect_url(request, reverse('cricket_team_registration')))

#         if TeamMemberVacancy.objects.filter(cricket_team=self.team).exists():
#             return redirect(self.get_redirect_url(request, reverse('cricket_team_wall', kwargs={'slug': self.team.slug})))

#         return super(TeamMemberVacancyRequestMixin, self).dispatch(request, *args, **kwargs)

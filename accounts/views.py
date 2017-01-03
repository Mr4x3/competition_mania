# Python Imports
import json
import uuid
from datetime import datetime

# Django Imports
from django.views.generic import View, FormView, TemplateView, RedirectView, DetailView, ListView
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import login, logout
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Count
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, get_object_or_404, render

# Third Party Django Imports

# Inter App Imports
# from competition_mania.shared.common_mixins import EmailNotVerifiedMixin, EmailVerifiedMixin, LoginRequiredMixin, UserProfileMidoutRequiredMixin, SportsProfileRequiredMixin, TokenAutoLoginMixin, ImageCropperMixin, CheckLoggedInMixin, UserProfileRequiredMixin, CompleteCricketerRequiredMixin, SuperUserRequiredMixin
from competition_mania.shared.common_mixins import CheckLoggedInMixin, TokenAutoLoginMixin
# from cricket.models import Cricketer, CricketTeam, CricketMatch
# from lookup.choices import STATE_TO_CITY_CHOICES

# Local Imports
# from .forms import LoginForm, UserRegistrationForm, ProfileSpecificRegistrationForm, ChangePasswordForm, EditUserProfileForm, LoginAsUserForm
# from .models import User, UserWallPost, Message, FriendRequest
from .utils import encode_token, decode_token, send_email_verification_mail, get_first_and_last_name, send_admin_mail_on_user_profile_completion
from .forms import UserRegistrationForm, LoginForm, ChangePasswordForm
from .models import User

class HomePageView(TemplateView):
    template_name = 'accounts/home_page.html'

class RegistrationView(TemplateView):
    """
    Main Home Page
    """

    template_name = 'accounts/homepage.html'

    def get_context_data(self, **kwargs):
        context = super(RegistrationView, self).get_context_data(**kwargs)
        # context['cricketer_list'] = Cricketer.objects.annotate(match_count=Count('teams__matches')).order_by('-match_count')[:4]
        # context['cricketteam_list'] = CricketTeam.objects.annotate(match_count=Count('team_matches')).order_by('-match_count')[:4]
        # context['start_date'] = datetime(1900, 1, 1)
        # context['end_date'] = datetime(9999, 12, 31)
        # context['login_form'] = LoginForm(prefix='login')
        context['registration_form'] = UserRegistrationForm(prefix='registration')
        # context['next_url'] = self.request.GET.get('next', '')
        return context

    # def get_post_login_redirect_url(self, user):
    #     next_url = self.request.GET.get('next', '')
    #     if next_url:
    #         return next_url
    #     return reverse_lazy('my_wall')

    def post(self, request, *args, **kwargs):
        # Instantiate Both Forms As Unbound Using Prefix
        # login_form    = LoginForm(prefix='login')

        # Bind the Relevant Form with Post Data
        registration_form = UserRegistrationForm(request.POST, prefix='registration')
        if registration_form.is_valid():
            user = registration_form.save()
            send_email_verification_mail(user, host=request.get_host())
            # user.backend = 'accounts.backends.EmailAuthenticationBackend'
            # login(request, user)
            return HttpResponseRedirect(reverse_lazy('home_page'))

        # In Case of Errors, Reload the Page with Context
        context = {
            'registration_form': registration_form,
        }
        return self.render_to_response(context)


# class FacebookLogin(View):

#     def post(self, request, *args, **kwargs):
#         if request.user.is_authenticated():
#             return HttpResponse(json.dumps({'status': 'SUCCESS'}))

#         email = request.POST.get('email', '')
#         name = request.POST.get('name', '')
#         first_name, last_name = get_first_and_last_name(name)
#         gender = 'F' if request.POST.get('gender', '').lower() == 'female' else 'M'
#         mobile = request.POST.get('mobile', '')
#         facebook_id = request.POST.get('id')
#         random_uuid = str(uuid.uuid4()).replace("-", "")[:8]

#         try:
#             if email:
#                 user = User.objects.filter(email=email).first()
#                 if user:
#                     user.backend = 'accounts.backends.EmailAuthenticationBackend'
#                     login(request, user)
#                     return HttpResponse(json.dumps({'status': 'SUCCESS'}))
#                 else:
#                     password = random_uuid
#                     user = User.objects.create_user(email=email, password=random_uuid, first_name=first_name, last_name=last_name, gender=gender, mobile=mobile, registration_source=2, is_email_verified=1)
#                     user = user.backend = 'accounts.backends.EmailAuthenticationBackend'
#                     login(request, user)
#                     return HttpResponse(json.dumps({'status': 'SUCCESS'}))

#             if mobile:
#                 user = User.objects.filter(mobile=mobile).first()
#                 if user:
#                     user.backend = 'accounts.backends.MobileAuthenticationBackend'
#                     login(request, user)
#                     return HttpResponse(json.dumps({'status': 'SUCCESS'}))

#             if facebook_id:
#                 user = User.objects.filter(social_profile_id=facebook_id).first()
#                 if user:
#                     user.backend = 'accounts.backends.SocialProfileIdAuthenticationBackend'
#                     login(request, user)
#                     return HttpResponse(json.dumps({'status': 'SUCCESS'}))

#             dummy_email = 'dummyemail{}fb@sportsvitae.com'.format(random_uuid)
#             user = User.objects.create_user(email=dummy_email, password=random_uuid, first_name=first_name, last_name=last_name, gender=gender, mobile=mobile, registration_source=2, is_email_verified=1, social_profile_id=facebook_id)
#             user.backend = 'accounts.backends.EmailAuthenticationBackend'
#             login(request, user)
#             return HttpResponse(json.dumps({'status': 'SUCCESS'}))

#         except Exception as e:
#             return HttpResponse(json.dumps({'status': 'FAILURE', 'error': repr(e)}))


# class GooglePlusLogin(View):

#     def post(self, request, *args, **kwargs):
#         if request.user.is_authenticated():
#             return HttpResponse(json.dumps({'status': 'SUCCESS'}))

#         email = request.POST.get('email', '')
#         name = request.POST.get('name', '')
#         first_name, last_name = get_first_and_last_name(name)
#         gender = request.POST.get('gender', 'M')
#         gmail_id = request.POST.get('id')
#         random_uuid = str(uuid.uuid4()).replace("-", "")[:8]
#         try:
#             if email:
#                 user = User.objects.filter(email=email).first()
#                 if user:
#                     user.backend = 'accounts.backends.EmailAuthenticationBackend'
#                     login(request, user)
#                     return HttpResponse(json.dumps({'status': 'SUCCESS'}))
#                 else:
#                     password = random_uuid
#                     user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name, gender=gender, registration_source=3, is_email_verified=1, social_profile_id=gmail_id)
#                     user.backend = 'accounts.backends.EmailAuthenticationBackend'
#                     login(request, user)

#             if gmail_id:
#                 user = User.objects.filter(social_profile_id=gmail_id).first()
#                 if user:
#                     user.backend = 'accounts.backends.SocialProfileIdAuthenticationBackend'
#                     login(request, user)
#                     return HttpResponse(json.dumps({'status': 'SUCCESS'}))

#             dummy_email = 'dummyemail{}gplus@sportsvitae.com'.format(random_uuid)
#             user = User.objects.create_user(email=dummy_email, password=random_uuid, first_name=first_name, last_name=last_name, gender=gender, registration_source=3, is_email_verified=1, social_profile_id=gmail_id)
#             user.backend = 'accounts.backends.EmailAuthenticationBackend'
#             login(request, user)
#             return HttpResponse(json.dumps({'status': 'SUCCESS'}))

#         except Exception as e:
#             return HttpResponse(json.dumps({'status': 'FAILURE', 'error': repr(e)}))


# class EditUserProfileViewMixin(object):

#     image_fields = ['display_picture', 'cover_picture']

#     def get_form_kwargs(self):
#         kwargs = super(EditUserProfileViewMixin, self).get_form_kwargs()
#         kwargs.update({'instance': self.request.user})
#         return kwargs

#     def get_initial(self):
#         initial = super(EditUserProfileViewMixin, self).get_initial()
#         initial['name'] = self.request.user.name
#         return initial

#     def form_valid(self, form):
#         form.save()
#         return super(EditUserProfileViewMixin, self).form_valid(form)


# class ProfileSpecificRegistration(LoginRequiredMixin, EmailVerifiedMixin, UserProfileRequiredMixin, EditUserProfileViewMixin, ImageCropperMixin, FormView):

#     template_name = 'accounts/profile_specific_registration.html'
#     form_class = ProfileSpecificRegistrationForm
#     success_url = reverse_lazy('create_cricket_certification')

#     def form_valid(self, form):
#         send_admin_mail_on_user_profile_completion(new_user_email=form.cleaned_data['email'])
#         return super(ProfileSpecificRegistration, self).form_valid(form)


# class EditUserProfile(LoginRequiredMixin, EmailVerifiedMixin, SportsProfileRequiredMixin, EditUserProfileViewMixin, ImageCropperMixin, FormView):

#     template_name = 'accounts/edit_user_profile.html'
#     form_class = EditUserProfileForm
#     success_url = reverse_lazy('my_wall')

#     def get_context_data(self, *args, **kwargs):
#         context = super(EditUserProfile,  self).get_context_data(*args, **kwargs)
#         context['state_to_city_choices'] = json.dumps(STATE_TO_CITY_CHOICES)
#         return context


class LoginView(FormView):

    form_class = LoginForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('home_page')

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context['next_url'] = self.request.GET.get('next', '')
        return context

    def get_success_url(self):
        next_url = self.request.GET.get('next', '')
        if next_url:
            return next_url
        return reverse_lazy('home_page')

    def form_valid(self, form):
        user = form.get_authenticated_user()
        login(self.request, user)
        return super(LoginView, self).form_valid(form)


class LogoutView(FormView):

    form_class = LoginForm
    template_name = 'accounts/logout.html'
    success_url = reverse_lazy('my_wall')

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_authenticated_user()
        login(self.request, user)
        return super(LogoutView, self).form_valid(form)



# class UserWall(CompleteCricketerRequiredMixin, DetailView):

#     model = get_user_model()
#     template_name = 'accounts/user_wall.html'

#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         if self.object.id == self.request.user.id:
#             return HttpResponseRedirect(reverse_lazy('my_wall'))
#         return super(UserWall, self).get(request, *args, **kwargs)

#     def get_context_data(self, *args, **kwargs):
#         context = super(UserWall, self).get_context_data(*args, **kwargs)
#         context['user_wall_posts'] = self.post_paginator_one
#         context['user_friends_count'] = self.object.friends.all().count()
#         context['man_of_the_matches_count'] = CricketMatch.objects.filter(man_of_the_match__cricketer__user_id=self.viewed_user.id).count()
#         context['best_batsman_matches_count'] = CricketMatch.objects.filter(best_batsman__cricketer__user_id=self.viewed_user.id).count()
#         context['best_bowler_matches_count'] = CricketMatch.objects.filter(best_bowler__cricketer__user_id=self.viewed_user.id).count()
#         context['best_fielder_matches_count'] = CricketMatch.objects.filter(best_fielder__cricketer__user_id=self.viewed_user.id).count()
#         if not self.request.user.is_anonymous():
#             context['mutual_friend_request'] = FriendRequest.objects.filter(Q(from_user=self.request.user, to_user=self.object)| Q(from_user=self.object, to_user=self.request.user)).first()
#         return context

#     def post_paginator_one(self):
#         """
#         An Index Page Where We Can Lay Out How to Pull Off Twitter Style
#         Pagination.
#         """
#         # Pull the Data
#         wall_posts = self.object.get_all_user_wall_posts()
#         # Grab the First Page of 100 Items
#         paginator = Paginator(wall_posts, 10)
#         page_first = paginator.page(1)

#         # Pass Out the Data
#         context = {
#             "object_list": page_first.object_list,
#             "page": page_first,
#         }
#         return page_first


# class UserPost(LoginRequiredMixin, TemplateView):
#     """
#     Display One Post With Given id
#     """

#     template_name = 'accounts/user_post.html'

#     def get_context_data(self, **kwargs):
#         context = super(UserPost, self).get_context_data(**kwargs)
#         id = kwargs.get('id')
#         post = UserWallPost.objects.get(id=id)
#         context['post'] = post
#         return context


# class ConnectRequestsView(LoginRequiredMixin, EmailVerifiedMixin, SportsProfileRequiredMixin, TemplateView):
#     """
#     Displays All the Pending Friend Requests.
#     """

#     template_name = 'accounts/pending_friend_requests.html'

#     def get_context_data(self):
#         context = super(ConnectRequestsView, self).get_context_data()
#         context['pending_friend_requests'] = self.request.user.get_all_friend_requests()
#         return context


# class ConnectionsView(LoginRequiredMixin, EmailVerifiedMixin, SportsProfileRequiredMixin, TemplateView):
#     """
#     Displays All the Connections I.e. All the Friends of a User.
#     """

#     template_name = 'accounts/my_connections.html'

#     def get_context_data(self):
#         context = super(ConnectionsView, self).get_context_data()
#         context['friends'] = self.request.user.friends.all()
#         return context


# class UserConnectionsView(SportsProfileRequiredMixin, DetailView):
#     """
#     Displays All the Connections I.e. All the Friends of a User.
#     """

#     model = get_user_model()
#     template_name = 'accounts/user_connections.html'

#     def get(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         if self.object.id == self.request.user.id:
#             return HttpResponseRedirect(reverse_lazy('connections'))
#         return super(UserConnectionsView, self).get(request, *args, **kwargs)

#     def get_context_data(self, **kwargs):
#         context = super(UserConnectionsView, self).get_context_data(**kwargs)
#         context['user_friends'] = self.object.friends.all()
#         return context


# class UserMessagesView(LoginRequiredMixin, EmailVerifiedMixin, SportsProfileRequiredMixin, TemplateView):
#     """
#     Displays All the Messages of a User.
#     """

#     template_name = 'accounts/user_messages.html'

#     def get_context_data(self):
#         context = super(UserMessagesView, self).get_context_data()
#         context['all_friends_messaged'] = self.request.user.get_all_friends_messaged()
#         context['last_messaged_friend_messages'] = self.request.user.get_last_messaged_friend_messages()
#         return context


# class FriendMessagesView(LoginRequiredMixin, EmailVerifiedMixin, SportsProfileRequiredMixin, DetailView):
#     """
#     Used When a User Clicks On a Friend's Message From the Site Header.
#     """

#     model = get_user_model()
#     template_name = 'accounts/user_messages.html'

#     def get_context_data(self, **kwargs):
#         context = super(FriendMessagesView, self).get_context_data()
#         context['all_friends_messaged'] = self.request.user.get_all_friends_messaged()
#         context['clicked_friend_messages'] = self.chat_history
#         return context

#     def get_object(self):
#         if hasattr(self, 'object'):
#             return self.object
#         return super(FriendMessagesView, self).get_object()

#     def get(self, request, *args, **kwargs):
#         # Redirect If No Message Exists Between the Two
#         self.object = self.get_object()
#         self.chat_history = list(self.request.user.get_chat_between_friend(friend=self.object))
#         if not self.chat_history:
#             return HttpResponseRedirect(reverse_lazy('user_messages'))

#         return super(FriendMessagesView, self).get(request, *args, **kwargs)


# class UserNotificationsView(LoginRequiredMixin, EmailVerifiedMixin, SportsProfileRequiredMixin, TemplateView):
#     """
#     Displays All the Notifications of a User.
#     """

#     template_name = 'accounts/user_notifications.html'

#     def get_context_data(self):
#         context = super(UserNotificationsView, self).get_context_data()
#         context['all_user_notifications'] = self.request.user.get_all_user_notifications()
#         return context


# class FriendSuggestionsView(LoginRequiredMixin, EmailVerifiedMixin, SportsProfileRequiredMixin, TemplateView):

#     template_name = 'accounts/friend_suggestions.html'


class EmailVerification(TokenAutoLoginMixin, RedirectView):

    url = reverse_lazy('cricket_profile_registration')
    permanent = False

    def get(self, request, *args, **kwargs):
        # Verify User Email
        self.request.user.is_email_verified = True
        self.request.user.save()

        # Show One Time Message
        messages.add_message(request, messages.INFO, 'Your email has been successfully verified.')

        return super(EmailVerification, self).get(request, *args, **kwargs)


# class VerifyEmail(LoginRequiredMixin, EmailNotVerifiedMixin, TemplateView):

#     template_name = 'accounts/verify_email.html'


class ChangePassword(TokenAutoLoginMixin, FormView):

    form_class = ChangePasswordForm
    template_name = 'accounts/change_password.html'
    success_url = reverse_lazy('home_page')

    def form_valid(self, form):
        self.request.user.set_password(form.cleaned_data['password1'])
        self.request.user.save()

        # Show One Time Message
        messages.add_message(self.request, messages.INFO, 'Your password has been successfully changed.')

        return super(ChangePassword, self).form_valid(form)


# class LoginAsUserView(SuccessMessageMixin, SuperUserRequiredMixin, FormView):
#     """
#     Used by Super User To Login To Any Other User Account
#     """

#     template_name = 'accounts/login_as.html'
#     form_class = LoginAsUserForm
#     success_url = reverse_lazy('my_wall')
#     success_message = "You Have Login To Another Account"

#     def form_valid(self, form):
#         username = form.cleaned_data['username']
#         user = get_object_or_404(User, email=username)
#         user.backend = 'accounts.backends.EmailAuthenticationBackend'
#         # Its Super User So Not Cheking Is Active
#         login(self.request, user)
#         return super(LoginAsUserView, self).form_valid(form)

# Python Imports

# Django Imports
from django.conf.urls import url, include

# Third Party Django Imports

# Inter App Imports

# Local Imports

# from .views import HomePage, MyWall, UserWall, LoginView, LogoutView, ProfileSpecificRegistration, ConnectionsView, UserMessagesView, FriendMessagesView, EmailVerification, ChangePassword, VerifyEmail, EditUserProfile, ConnectRequestsView, FacebookLogin, GooglePlusLogin, FriendSuggestionsView, UserNotificationsView, UserConnectionsView, UserPost, LoginAsUserView
from .views import RegistrationView, LoginView, HomePageView, EmailVerification, ChangePassword, LogoutView

urlpatterns = [
    url(r'^$', HomePageView.as_view(), name='home_page'),
    url(r'register/$', RegistrationView.as_view(), name='registration'),
    # url(r'^login-as/$', LoginAsUserView.as_view(), name='login_as'),  # Login As User View
    # url(r'^profile/$', MyWall.as_view(), name='my_wall'),
    # url(r'^profile/edit/$', EditUserProfile.as_view(), name='edit_user_profile'),
    # url(r'^profile/(?P<slug>[\w-]+)/$', UserWall.as_view(), name='user_wall'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    # url(r'^registration/profile/$', ProfileSpecificRegistration.as_view(), name='profile_specific_registration'),
    # url(r'^connect-requests/$', ConnectRequestsView.as_view(), name='pending_friend_requests'),
    # url(r'^connections/$', ConnectionsView.as_view(), name='connections'),
    # url(r'^connections/(?P<slug>[\w-]+)/$', UserConnectionsView.as_view(), name='user_connections'),
    # url(r'^messages/$', UserMessagesView.as_view(), name='user_messages'),
    # url(r'^messages/(?P<slug>[\w-]+)/$', FriendMessagesView.as_view(), name='friend_messages'),
    # url(r'^friend-suggestions/$', FriendSuggestionsView.as_view(), name='friend_suggestions'),
    # url(r'^notifications/$', UserNotificationsView.as_view(), name='user_notifications'),
    # url(r'^verify-email/$', VerifyEmail.as_view(), name='verify_email'),
    url(r'^email-verification/(?P<token>.+)/$', EmailVerification.as_view(), name='email_verification'),
    url(r'^change-password/(?P<token>.+)/$', ChangePassword.as_view(), name='change_password'),
    # url(r'^login/facebook/$', FacebookLogin.as_view(), name='facebook_login'),
    # url(r'^login/google-plus/$', GooglePlusLogin.as_view(), name='google_plus_login'),
    # url(r'^user/post/(?P<id>[0-9]+)/$', UserPost.as_view(), name='user-post'),
    # # Post Paginator
    # url(r'^user_posts/(?P<page>[0-9]+)/', MyWall.post_paginator_json, name='user_post_wall'),
    # # Include Api Urls
    # url(r'^api/', include('accounts.api.urls')),

]

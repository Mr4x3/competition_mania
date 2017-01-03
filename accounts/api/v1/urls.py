# Python Imports

# Django Imports
from django.conf.urls import url, include

# Third Party Django Imports
from rest_framework.routers import DefaultRouter

# Inter App Imports

# Local Imports
from .views import SendFriendRequest, MarkFriendRequestsViewed, AcceptFriendRequest, RejectFriendRequest, CancelFriendRequest, UnfriendUser, UserMessages, MarkUserMessagesRead, DeleteFriendChatHistory, ForgotPassword, ResendVerificationMail, UserWallPostCreateDestroyViewSet, UserWallPostCommentLikeView, UserWallPostCommentUnlikeView, UserWallPostCommentDestroyView, MarkUserNotificationsViewed, OtherUserPosts, UserTourCompleted, UserTourCompletedStatus

router = DefaultRouter()
router.register(r'user-wall-posts', UserWallPostCreateDestroyViewSet, base_name='user_wall_post')

urlpatterns = [
    url(r'^', include(router.urls)),
    # Friend Requests
    url(r'^friend-requests/$', SendFriendRequest.as_view(), name='send_friend_request'),
    url(r'^friend-requests/mark-viewed/$', MarkFriendRequestsViewed.as_view(), name='mark_friend_requests_viewed'),
    url(r'^friend-requests/(?P<id>\d+)/accept/$', AcceptFriendRequest.as_view(), name='accept_friend_request'),
    url(r'^friend-requests/(?P<id>\d+)/reject/$', RejectFriendRequest.as_view(), name='reject_friend_request'),
    url(r'^friend-requests/(?P<id>\d+)/cancel/$', CancelFriendRequest.as_view(), name='cancel_friend_request'),
    url(r'^unfriend/$', UnfriendUser.as_view(), name='unfriend'),
    url(r'^messages/$', UserMessages.as_view(), name='user_messages_api'),
    url(r'^messages/mark-read/$', MarkUserMessagesRead.as_view(), name='mark_user_messages_viewed'),
    url(r'^friends/(?P<id>\d+)/messages/$', DeleteFriendChatHistory.as_view(), name='delete_friend_chat_history'),
    url(r'^notifications/mark-viewed/$', MarkUserNotificationsViewed.as_view(), name='mark_user_notifications_viewed'),
    url(r'^forgot-password/$', ForgotPassword.as_view(), name='forgot_password'),
    url(r'^resend-verification-mail/$', ResendVerificationMail.as_view(), name='resend_verification_mail'),
    # Wall Post Comments
    url(r'^user-wall-post-comments/(?P<pk>\d+)/$', UserWallPostCommentDestroyView.as_view(), name='user_wall_post_comment_delete'),
    url(r'^user-wall-post-comments/(?P<pk>\d+)/like/$', UserWallPostCommentLikeView.as_view(), name='user_wall_post_comment_like'),
    url(r'^user-wall-post-comments/(?P<pk>\d+)/unlike/$', UserWallPostCommentUnlikeView.as_view(), name='user_wall_post_comment_unlike'),
    url(r'^user-posts/(?P<slug>[\w-]+)/$', OtherUserPosts.as_view(), name='any-user_post_wall'),
    url(r'^tour-completed/(?P<id>\d+)/$', UserTourCompleted.as_view(), name='tour-completed'),
    url(r'^tour-completed-status/(?P<id>\d+)/$', UserTourCompletedStatus.as_view(), name='tour-completed-status'),

]

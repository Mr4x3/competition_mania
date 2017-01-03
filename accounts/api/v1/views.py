# Python Imports
from itertools import chain

# Django Imports
from django.http import Http404
from django.db.models import Q

# Third Party Django Imports
from rest_framework.generics import  GenericAPIView, CreateAPIView, UpdateAPIView, ListCreateAPIView, DestroyAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import exceptions
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin
from rest_framework.decorators import detail_route
from rest_framework.pagination import PageNumberPagination

# Inter App Imports
from sportsvitae.shared.common_mixins import EmailVerifiedMixin, LoginRequiredMixin
from cricket.models import CricketTeamWallPost
from sportsvitae.shared.rest_addons import CreateDestroyViewSet
from cricket.api.v1.serializers import CricketTeamWallPostSerializer
from accounts.models import FriendRequest, Message, UserWallPost, UserWallPostComment, UserNotification, User
from accounts.utils import send_forgot_password_mail, send_email_verification_mail

# Local Imports
from .serializers import FriendRequestSerializer, UnfriendUserSerializer, SendMessageSerializer, ForgotPasswordSerializer, UserWallPostSerializer, UserWallPostCommentSerializer, MyWallPostSerializer, UserTourCompletedSerializer
from .pagination import PostLimitOffsetPagination, PostPageNumberPagination


class UserTourCompleted(UpdateAPIView):
    """
    For Switching The Status Of Tour Completed
    URL: <host>/api/v1/accounts/tour-completed/27/
    Method Allowed: ["GET"]
    """

    permission_classes = [IsAuthenticated, ]
    serializer_class = UserTourCompletedSerializer

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('id')
        status = dict()
        instance = User.objects.filter(id=user_id)[0]

        if instance != request.user:
            status['status'] = 'Forbidden'
            return Response(status, status=201)
        if not instance.tour_completed:
            instance.tour_completed = True
        else:
            instance.tour_completed = False
        instance.save()

        status['status'] = instance.tour_completed
        return Response(status, status=201)


class UserTourCompletedStatus(APIView):

    """
    For Getting Tour Status Of The player
    URL: <host>/api/v1/accounts/tour-completed-status/27/
    Method Allowed: ["GET"]
    """

    permission_classes = [IsAuthenticated, ]
    serializer_class = UserTourCompletedSerializer

    def get(self, request, *args, **kwargs):
        user_id = self.kwargs.get('id')
        status = dict()
        instance = User.objects.get(id=user_id)

        if instance != request.user:
            status['status'] = 'Forbidden'
            return Response(status, status=201)
        status['status'] = instance.tour_completed
        return Response(status, status=201)


class SendFriendRequest(CreateAPIView):
    """
    Sends a friend request.
    URL:
    Accepted Method: ["POST"]
    """

    permission_classes = [IsAuthenticated, ]
    serializer_class = FriendRequestSerializer


class AcceptFriendRequest(APIView):
    """
    Accept a friend request.
    URL:
    Accepted Method: ["POST"]
    """

    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        friend_request = list(FriendRequest.objects.filter(id=self.kwargs.get('id')))

        if not friend_request:
            raise Http404

        friend_request = friend_request[0]

        if friend_request.to_user != request.user:
            raise exceptions.PermissionDenied()

        friend_request.accept()  # Accept Friend Request

        # Send Notifications
        UserNotification.create_friend_request_accept_notification(friend_request.from_user, friend_request.to_user)

        return Response()


class RejectFriendRequest(APIView):
    """
    Reject a friend request.
    URL:
    Accepted Method: ["POST"]
    """

    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        friend_request = list(FriendRequest.objects.filter(id=self.kwargs.get('id')))

        if not friend_request:
            raise Http404

        friend_request = friend_request[0]

        if friend_request.to_user != request.user:
            raise exceptions.PermissionDenied()

        friend_request.reject()  # Reject Friend Request
        return Response()


class CancelFriendRequest(APIView):
    """
    Cancel a Friend Request.
    URL:
    Accepted Method: ["POST"]
    """

    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        friend_request = list(FriendRequest.objects.filter(id=self.kwargs.get('id')))

        if not friend_request:
            raise Http404

        friend_request = friend_request[0]

        if friend_request.from_user != request.user:
            raise exceptions.PermissionDenied()

        friend_request.cancel()  # Cancel Friend Request
        return Response()


class UnfriendUser(CreateAPIView):
    """
    Unfriend a friend.
    URL:
    Accepted Method: ["POST"]
    """

    permission_classes = [IsAuthenticated, ]
    serializer_class = UnfriendUserSerializer

    def perform_create(self, serializer):
        self.request.user.remove_friend(serializer.friend)  # Unfriend

        # Delete Existing Friend Requests
        FriendRequest.objects.filter(Q(from_user=self.request.user, to_user=serializer.friend) | Q(from_user=serializer.friend, to_user=self.request.user)).delete()


class MarkFriendRequestsViewed(APIView):
    """
    Mark friend requests as viewed.
    URL:
    Accepted Method: ["POST"]
    """

    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        friend_request_ids = request.data.getlist('friend_requests_viewed[]', [])

        if not friend_request_ids:
            return Response(data={'friend_requests_viewed': 'This field is required.'}, status=400)

        FriendRequest.objects.filter(to_user=request.user, id__in=friend_request_ids).update(viewed=True)

        return Response(status=201)


class UserMessages(ListCreateAPIView):
    """
    1. Sends a new message to a friend.
            Accepted Method: ["POST"]

    2. Lists messages between a friend.
        Accepted Method: ["GET"]

    URL:
    """

    permission_classes = [IsAuthenticated, ]
    serializer_class = SendMessageSerializer

    def get_queryset(self):
        friend_id = self.request.query_params.get('friend_id')
        if not friend_id:
            return Message.objects.none()
        return Message.objects.filter(Q(sender=self.request.user, recipient_id=friend_id, deleted_by_sender=False) | Q(sender_id=friend_id, recipient=self.request.user, deleted_by_recipient=False))


class MarkUserMessagesRead(APIView):
    """
    Mark Messages As Read.
    URL:
    Accepted Method: ["POST"]
    """

    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        message_sender_ids = request.data.getlist('message_sender_ids[]', [])
        if not message_sender_ids:
            return Response(data={'message_sender_ids': 'This field is required.'}, status=400)
        Message.objects.filter(recipient=request.user, sender_id__in=message_sender_ids).update(unread=False)

        return Response(status=201)


class DeleteFriendChatHistory(DestroyAPIView):
    """
    Delete Chat History with Friend.
    URL:
    Accepted Method: ["DELETE""]  # Cause Problem If One ''
    """

    permission_classes = [IsAuthenticated, ]

    def delete(self, request, *args, **kwargs):
        friend_id = self.kwargs['id']

        if not self.request.user.friends.filter(id=friend_id).exists():
            return Response(status=404)

        # Set Deleted Flag For Sent Messages
        Message.objects.filter(sender=self.request.user, recipient_id=friend_id).update(deleted_by_sender=True)

        # Set Deleted Flag For Received Messages
        Message.objects.filter(sender_id=friend_id, recipient=self.request.user).update(deleted_by_recipient=True)

        return Response(status=204)


class MarkUserNotificationsViewed(APIView):
    """
    Mark user notifications as viewed.
    URL:
    Accepted Method: ["POST"]
    """

    permission_classes = [IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        user_notification_ids = request.data.getlist('user_notifications_viewed[]', [])

        if not user_notification_ids:
            return Response(data={'user_notifications_viewed': 'This field is required.'}, status=400)

        UserNotification.objects.filter(id__in=user_notification_ids).update(viewed=True)

        return Response(status=201)


class ForgotPassword(CreateAPIView):
    """
    Forgot Password
    URL:
    Accepted Method: ["POST"]
    """

    serializer_class = ForgotPasswordSerializer

    def perform_create(self, serializer):
        send_forgot_password_mail(user=serializer.user, host=self.request._request.get_host())


class ResendVerificationMail(APIView):
    """
    Resend Email Verification Mail
    URL:
    Accepted Method: ["GET"]
    """

    permission_classes = [IsAuthenticated, ]

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_email_verified:
            send_email_verification_mail(user=self.request.user, host=self.request._request.get_host())
        return Response()


class UserWallPostCreateDestroyViewSet(CreateDestroyViewSet):
    """
    Create And Delete a User Wall Post.
    URL:
    Accepted Method:  ["POST", "DELETE""]
    """

    permission_classes = [IsAuthenticated, ]
    serializer_class = UserWallPostSerializer

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        if self.action in ['like', 'unlike', 'comments']:
            return UserWallPost.objects.all()

        return UserWallPost.objects.filter(owner=self.request.user)

    @detail_route(methods=['post'])
    def like(self, request, pk=None):
        """
        Records a User Like On a User Wall Post.
        """

        user_wall_post = self.get_object()
        user_wall_post.likes.add(self.request.user)
        to_user = user_wall_post.owner
        from_user = request.user

        UserNotification.create_post_friend_liked_notification(from_user, to_user, 'Right', id=pk)
        return Response(status=201)

    @detail_route(methods=['post'])
    def unlike(self, request, pk=None):
        """
        Unlikes a user like on a user wall post.
        """

        user_wall_post = self.get_object()
        user_wall_post.likes.remove(self.request.user)
        return Response(status=201)

    @detail_route(methods=['get', 'post'])
    def comments(self, request, pk=None):
        """
        GET --> Returns All the Comments On a User Wall Post.
        POST --> Records a User Comment On a User Wall Post.
        """

        if request.method == 'GET':
            user_wall_post = self.get_object()
            post_comments = UserWallPostComment.objects.filter(user_wall_post=user_wall_post)
            post_comment_serializer = UserWallPostCommentSerializer(post_comments, many=True)
            return Response(post_comment_serializer.data)

        user_wall_post = self.get_object()
        post_comment_serializer = UserWallPostCommentSerializer(data=request.data)
        post_comment_serializer.is_valid(raise_exception=True)
        post_comment_serializer.save(comment_by=self.request.user, user_wall_post=user_wall_post)

        to_user = user_wall_post.owner
        from_user = request.user
        UserNotification.create_post_friend_comment_notification(from_user, to_user, 'Right', id=pk)
        return Response(data=post_comment_serializer.data, status=201)


class UserWallPostCommentLikeView(GenericAPIView):
    """
    View For User Wall Post Like Comment Update
    URL:
    Accepted Methods: ["POST"]
    """

    permission_classes = [IsAuthenticated, ]
    queryset = UserWallPostComment.objects.all()

    def post(self, request, *args, **kwargs):
        """
        Records a user like on a user wall post comment.
        """

        user_wall_post_comment = self.get_object()
        user_wall_post_comment.likes.add(self.request.user)
        return Response(status=201)


class UserWallPostCommentUnlikeView(GenericAPIView):
    """
    View For User Wall Post Like UnComment Update
    URL:
    Accepted Methods: ["POST"]
    """

    permission_classes = [IsAuthenticated, ]
    queryset = UserWallPostComment.objects.all()

    def post(self, request, *args, **kwargs):
        """
        Unlikes a user like on a user wall post comment.
        """

        user_wall_post_comment = self.get_object()
        user_wall_post_comment.likes.remove(self.request.user)
        return Response(status=201)


class UserWallPostCommentDestroyView(DestroyAPIView):
    permission_classes = [IsAuthenticated, ]

    def get_queryset(self):
        return UserWallPostComment.objects.filter(comment_by=self.request.user)


class UserPosts(ListAPIView):
    """
    Api for pagination of posts
    URL: <host>/api/v1/accounts/user-posts/
    Allowed Methods: ["GET"]
    """

    serializer_class = UserWallPostSerializer
    # filter_backends= [SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated, ]
    # search_fields = ['title', 'content', 'user__first_name']
    pagination_class = PostPageNumberPagination  # PageNumberPagination

    def get_queryset(self, *args, **kwargs):
        # queryset_list = super(PostListAPIView, self).get_queryset(*args, **kwargs)
        queryset_list = UserWallPost.objects.all().filter(owner=self.request.user)
        # query = self.request.GET.get("q")
        # if query:
        #     queryset_list = queryset_list.filter(
        #             Q(title__icontains=query)|
        #             Q(content__icontains=query)|
        #             Q(user__first_name__icontains=query) |
        #             Q(user__last_name__icontains=query)
        #             ).distinct()
        return queryset_list


class OtherUserPosts(ListAPIView):
    """
    Api for pagination of posts
    URL: <host>/api/v1/accounts/user-posts/test2-2-24/
    Allowed Methods: ["GET"]
    """

    serializer_class = MyWallPostSerializer
    # filter_backends= [SearchFilter, OrderingFilter]
    permission_classes = [IsAuthenticated, ]
    pagination_class = PostPageNumberPagination  # PageNumber Pagination

    def get_queryset(self, *args, **kwargs):
        slug = self.kwargs['slug']
        user = User.objects.filter(slug=slug)[0]

        # self.request.user.get_all_cricket_team_posts_for_user_wall()
        userwall = user.get_all_user_posts_for_user_wall()
        teamwall = list()
        for i in user.get_all_cricket_team_posts_for_user_wall():
            i.owner = i.team
            teamwall.append(i)
        queryset_list = list(chain(userwall, teamwall))  # Combine the Two Querysets :]
        queryset_list = sorted(queryset_list, key=lambda x: x.posted_on, reverse=True)
        for instance in queryset_list:
            instance.self_like = self.request.user
        # queryset_list = user.get_all_user_posts_for_user_wall()

        return queryset_list


# class OtherUserPostsx(LoginRequiredMixin, ListAPIView):
#     """
#     Dont Do This It Sucks This Tell How Bad Code Is Written :[
#     """
#
#     serializer_class = UserWallPostSerializer
#     pagination_class = PostPageNumberPagination  # PageNumberPagination
#
#     def list(self, request, *args, **kwargs):
#         slug = self.kwargs['slug']
#         user = User.objects.filter(slug=slug)[0]
#         userwall = user.get_all_user_posts_for_user_wall()
#         teamwall = user.get_all_cricket_team_posts_for_user_wall()
#
#         results = list()
#         entries = list(chain(userwall, teamwall))  # Combine the Two Querysets
#
#         for entry in entries:
#             type = entry.__class__.__name__.lower()  # 'nurse', 'pilot'
#             if isinstance(entry, CricketTeamWallPost):
#                 serializer = CricketTeamWallPostSerializer(entry)
#                 id=serializer.data['id']
#                 text=serializer.data['text']
#                 post_image=serializer.data['post_image']
#                 location=serializer.data['location']
#                 post_type=serializer.data['post_type']
#
#                 posted_by_user_slug=serializer.data['posted_by_user_slug']
#                 dictionary = {'id':id, 'text':text, 'post_image':post_image, 'location':location, 'post_type':post_type, 'posted_by_user_slug':posted_by_user_slug}
#             if isinstance(entry, UserWallPost):
#
#                 serializer = UserWallPostSerializer(entry)
#                 id=serializer.data['id']
#                 text=serializer.data['text']
#                 post_image=serializer.data['post_image']
#                 location=serializer.data['location']
#                 post_type=serializer.data['post_type']
#                 posted_by_user_slug=serializer.data['posted_by_user_slug']
#                 dictionary = {'id':id, 'text':text, 'post_image':post_image, 'location':location, 'post_type':post_type, 'posted_by_user_slug':posted_by_user_slug}
#             results.append(dictionary)
#         return Response(results)

# Python Imports

# Django Imports

# Third Party Django Imports

# Inter App Imports

# Local Imports
from .models import FriendRequest, Message, UserNotification


def header_context(request):
    """
    Adds Latest Messages And Connect Requests to the Context of a Page.
    """
    if not request.user.is_authenticated() or not request.user.is_complete_user():
        return {}

    friends = list(request.user.friends.all())

    friend_requests_notification_count = FriendRequest.objects.filter(to_user=request.user, accepted=False, viewed=False).count()

    messages_notification_count = Message.objects.filter(recipient=request.user, unread=True, deleted_by_recipient=False).values_list('sender', flat=True).distinct().count()

    user_notifications_count = UserNotification.objects.filter(user=request.user, viewed=False).count()

    return {
        'latest_friend_requests': request.user.get_latest_friend_requests(),
        'friend_requests_notification_count': friend_requests_notification_count,
        'latest_received_messages': request.user.get_latest_received_messages(),
        'messages_notification_count': messages_notification_count,
        'latest_user_notifications': request.user.get_latest_user_notifications(),
        'user_notifications_count': user_notifications_count,
        'friend_suggestions': request.user.get_friend_suggestions(),
        'team_follow_suggestions': request.user.get_team_follow_suggestions(),
        'friends': friends,
        'friends_count': len(friends),
    }

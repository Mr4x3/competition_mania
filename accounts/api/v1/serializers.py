# Python Imports

# Django Imports

# Third Party Django Imports
from rest_framework import serializers

# Inter App Imports
from accounts.models import FriendRequest, User, Message, UserWallPost, UserWallPostComment
from cricket.models import CricketTeamWallPost

# Local Imports


class FriendRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user']
        extra_kwargs = {'id': {'read_only': True}}

    def __init__(self, *args, **kwargs):
        super(FriendRequestSerializer, self).__init__(*args, **kwargs)
        unique_together_validator = self.validators[0]
        unique_together_validator.message = 'Friend request already sent to this user.'

    def validate_from_user(self, value):
        if self.context.get('request') and value != self.context['request'].user:
            raise serializers.ValidationError("Cannot send friend requests on behalf of others.")

        if not value.is_complete_user():
            raise serializers.ValidationError("Only fully registered users can send friend requests.")
        return value

    def validate_to_user(self, value):
        if not value.is_complete_user():
            raise serializers.ValidationError("Only fully registered users can receive friend requests.")
        return value

    def validate(self, data):
        if data['from_user'] == data['to_user']:
            raise serializers.ValidationError('User cannot send friend request to themselves.')

        if data['from_user'].friends.filter(id=data['to_user'].id).exists():
            raise serializers.ValidationError("Users are already friends")
        return data


class UnfriendUserSerializer(serializers.Serializer):

    friend_id = serializers.IntegerField()

    def validate_friend_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid friend id.")

        request = self.context.get('request')
        if not request:
            return value

        if request.user.id == value:
            raise serializers.ValidationError('You cannot unfriend yourself.')

        self.friend = request.user.friends.filter(id=value).first()
        if not self.friend:
            raise serializers.ValidationError("You are not currently friends with this user.")
        return value


class SendMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Message
        fields = ['id', 'sender', 'recipient', 'text', 'sent_on']
        extra_kwargs = {'id': {'read_only': True}}

    def validate_sender(self, value):
        if self.context.get('request') and value != self.context['request'].user:
            raise serializers.ValidationError("Cannot send messages on behalf of others.")

        if not value.is_complete_user():
            raise serializers.ValidationError("Only fully registered users can send messages.")
        return value

    def validate_recipient(self, value):
        if not value.is_complete_user():
            raise serializers.ValidationError("Only fully registered users can receive messages.")

        return value

    def validate(self, data):
        if data['sender'] == data['recipient']:
            raise serializers.ValidationError('Cannot send message to ourselves.')
        return data


class ForgotPasswordSerializer(serializers.Serializer):

    email = serializers.EmailField()

    def validate_email(self, value):
        users = list(User.objects.filter(email=value))
        if not users:
            raise serializers.ValidationError('This email is not registered with us.')
        self.user = users[0]
        return value


class UserWallPostSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)
    posted_by_user_slug = serializers.SerializerMethodField()

    class Meta:
        model = UserWallPost
        fields = ['id', 'text', 'post_image', 'location', 'post_type', 'posted_by_user_slug']

    def get_posted_by_user_slug(self, obj):
        return obj.owner.slug

    def check_valid_image_post(self, data):
        if not data.get('post_image'):
            raise serializers.ValidationError('Please upload a image.')

    def check_valid_location_post(self, data):
        if not data.get('location'):
            raise serializers.ValidationError('Please enter a location.')

    def validate(self, data):
        if data.get('post_type') == 1:  # Normal Post
            if not data.get('text'):
                raise serializers.ValidationError('Please enter some text.')
            data['post_image'] = None
            data['location'] = None

        elif data.get('post_type') == 2:  # Image Post
            self.check_valid_image_post(data)
            data['location'] = None

        elif data.get('post_type') == 3:  # Location Post
            self.check_valid_location_post(data)
            data['post_image'] = None

        return data


class UserWallPostCommentSerializer(serializers.ModelSerializer):

    comment_by_user_id = serializers.SerializerMethodField(method_name='get_user_id')
    comment_by_user_name = serializers.SerializerMethodField(method_name='get_user_name')
    comment_by_user_slug = serializers.SerializerMethodField(method_name='get_user_slug')
    comment_by_user_display_picture = serializers.SerializerMethodField(method_name='get_user_display_picture')

    class Meta:
        model = UserWallPostComment
        fields = ['id', 'comment', 'user_wall_post', 'commented_on', 'likes', 'comment_by_user_id', 'comment_by_user_slug', 'comment_by_user_name', 'comment_by_user_display_picture']
        extra_kwargs = {
            'user_wall_post': {'read_only': True},
            'commented_on': {'read_only': True},
            'id': {'read_only': True},
            'likes': {'read_only': True}
        }

    def get_user_id(self, obj):
        return obj.comment_by_id

    def get_user_name(self, obj):
        return obj.comment_by.name

    def get_user_slug(self, obj):
        return obj.comment_by.slug

    def get_user_display_picture(self, obj):
        try:
            image_url = obj.comment_by.display_picture.url
            return image_url
        except ValueError:
            return None


class MyWallPostSerializer(serializers.ModelSerializer):
    """
    Wall Post For Api Serializer
    """

    id = serializers.IntegerField(read_only=True)
    owner = serializers.SerializerMethodField()
    owner_id = serializers.SerializerMethodField()
    user_slug = serializers.SerializerMethodField()
    display_picture = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    no_of_comments = serializers.SerializerMethodField()
    if_team = serializers.SerializerMethodField()
    team_name = serializers.SerializerMethodField()
    team_id = serializers.SerializerMethodField()
    posted_by = serializers.SerializerMethodField()
    team_slug = serializers.SerializerMethodField()
    posted_on = serializers.SerializerMethodField()
    self_like = serializers.SerializerMethodField()

    class Meta:
        depth = 1
        model = UserWallPost
        fields = ['id', 'text', 'post_image', 'location', 'post_type', 'owner','if_team','team_name','team_id','team_slug','posted_on','posted_by','owner_id', 'user_slug','display_picture','likes', 'self_like', 'comments', 'no_of_comments']

    def get_owner(self, obj):
        try:
            if obj.team_id:
                return str(obj.posted_by.name)
        except:
            return obj.owner.name

    def get_likes(self, obj):
        try:
            # likes = int(obj.likes.count())
            liked_by_user = obj.likes.all()
            if liked_by_user:
                name_slug_list = [{"name": user.name, "slug": user.slug} for user in liked_by_user]
                return name_slug_list
        except:
            return 0

    def get_self_like(self, obj):
        try:
            if obj.self_like in obj.likes.all():
                return True
            else:
                return False
        except:
            return False

    def get_comments(self, obj):
        try:
            user_wall_comment = str(obj.user_wall_post_comments.all())
            return user_wall_comment
        except:
            return str(obj.cricket_team_wall_post_comments.all())

    def get_no_of_comments(self, obj):
        try:
            user_wall_comment = len(obj.user_wall_post_comments.all())
            return user_wall_comment
        except:
            return len(obj.cricket_team_wall_post_comments.all())

    def get_owner_id(self, obj):
        try:
            if obj.team_id:
                return obj.posted_by.id
        except:
            return obj.owner.id

    def get_user_slug(self, obj):
        try:
            if obj.team_id:
                return obj.posted_by.slug
        except:
                return obj.owner.slug

    def get_display_picture(self, obj):
        try:
            if obj.team_id:
                return str(obj.posted_by.display_picture)
        except:
            return str(obj.owner.display_picture)

    def get_if_team(self, obj):
        try:
            if obj.team_id:
                return True
        except:
            return False

    def get_team_name(self, obj):
        try:
            if obj.team_id:
                return obj.team.name
        except:
            return False

    def get_team_id(self, obj):
        try:
            if obj.team_id:
                return obj.team_id
        except:
            return False

    def get_team_slug(self, obj):
        try:
            if obj.team_id:
                return obj.team.slug
        except:
            return False

    def get_posted_on(self, obj):
        return obj.posted_on

    def get_posted_by(self, obj):
        try:
            if obj.team_id:
                return obj.posted_by.name
        except:
            return None


class UserTourCompletedSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['tour_completed']

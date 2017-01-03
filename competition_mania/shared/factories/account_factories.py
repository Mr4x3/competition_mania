# inbuilt python imports

# inbuilt django imports
from django.conf import settings

# third-party django imports
import factory

# inter-app imports
from accounts.models import User, FriendRequest, Message, UserWallPost, UserWallPostComment, UserNotification

# local imports


class UserFactory(factory.DjangoModelFactory):

    class Meta:
        model = User

    email = factory.Sequence(lambda i: "test{0}@test.com".format(i))
    password = factory.PostGenerationMethodCall('set_password', settings.TEST_USER_PASSWORD)
    first_name = 'Jon'
    last_name = 'Snow'
    mobile = '9999999999'
    country = 'IN'
    state = 1013
    city = 10178
    registration_midout = False
    is_email_verified = True
    # display_picture = factory.django.ImageField(from_path='accounts/tests/test_cover_pic.png')
    # cover_picture = factory.django.ImageField(from_path='accounts/tests/test_cover_pic.png')


class MidoutUserFactory(factory.DjangoModelFactory):

    class Meta:
        model = User

    email = factory.Sequence(lambda i: "test_midout{0}@test.com".format(i))
    password = factory.PostGenerationMethodCall('set_password', settings.TEST_USER_PASSWORD)
    first_name = 'Jon'
    last_name = 'Snow'
    is_email_verified = True


class ForeignUserFactory(factory.DjangoModelFactory):

    class Meta:
        model = User

    email = factory.Sequence(lambda i: "test{0}@test.com".format(i))
    password = factory.PostGenerationMethodCall('set_password', settings.TEST_USER_PASSWORD)
    first_name = 'Jon'
    last_name = 'Snow'
    mobile = '9999999999'
    country = 'US'
    state_text = 'Nevada'
    city_text = 'Las Vegas'
    registration_midout = False
    is_email_verified = True


class FriendRequestFactory(factory.DjangoModelFactory):

    class Meta:
        model = FriendRequest
        exclude = ('cricketer1', 'cricketer2')

    cricketer1 = factory.SubFactory('sportsvitae.shared.factories.CricketerFactory')
    cricketer2 = factory.SubFactory('sportsvitae.shared.factories.CricketerFactory')
    from_user = factory.LazyAttribute(lambda obj: obj.cricketer1.user)
    to_user = factory.LazyAttribute(lambda obj: obj.cricketer2.user)


class MessageFactory(factory.DjangoModelFactory):

    class Meta:
        model = Message
        exclude = ('cricketer1', 'cricketer2')

    cricketer1 = factory.SubFactory('sportsvitae.shared.factories.CricketerFactory')
    cricketer2 = factory.SubFactory('sportsvitae.shared.factories.CricketerFactory')
    sender = factory.LazyAttribute(lambda obj: obj.cricketer1.user)
    recipient = factory.LazyAttribute(lambda obj: obj.cricketer2.user)
    text = 'Valar Morghulis!'


class UserWallPostFactoryMixin(factory.DjangoModelFactory):

    class Meta:
        model = UserWallPost
        exclude = ('cricketer',)

    cricketer = factory.SubFactory('sportsvitae.shared.factories.CricketerFactory')
    owner = factory.LazyAttribute(lambda obj: obj.cricketer.user)

    @factory.post_generation
    def likes(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of users were passed in, add them
            for post_liked_by in extracted:
                self.likes.add(post_liked_by)


class UserWallPostFactory(UserWallPostFactoryMixin):

    text = 'Some wall post'
    post_type = 1


class UserWallImagePostFactory(UserWallPostFactoryMixin):

    text = 'Check out this new pic'
    post_image = factory.django.ImageField(from_path='accounts/tests/test_user_wall_post_image.jpg')
    post_type = 2


class UserWallLocationPostFactory(UserWallPostFactoryMixin):

    text = 'Checked in at'
    location = 'Delhi, India'
    post_type = 3


class UserWallPostCommentFactory(factory.DjangoModelFactory):

    class Meta:
        model = UserWallPostComment
        exclude = ('cricketer',)

    cricketer = factory.SubFactory('sportsvitae.shared.factories.CricketerFactory')
    comment_by = factory.LazyAttribute(lambda obj: obj.cricketer.user)
    user_wall_post = factory.SubFactory(UserWallPostFactory)
    comment = 'Nice post'

    @factory.post_generation
    def likes(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of users were passed in, add them
            for comment_liked_by in extracted:
                self.likes.add(comment_liked_by)


class FriendRequestAcceptNotificationFactory(factory.DjangoModelFactory):

    class Meta:
        model = UserNotification
        exclude = ('cricketer',)
 
    cricketer = factory.SubFactory('sportsvitae.shared.factories.CricketerFactory')
    user = factory.LazyAttribute(lambda obj: obj.cricketer.user)
    message = 'You and <b>Jon Snow</b> are now friends.'
    notification_type = 1

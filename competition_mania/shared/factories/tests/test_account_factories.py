# inbuilt python imports
import unittest
import os

# inbuilt django imports
from django.test import Client

# third-party django imports
import pytest

# inter-app imports
from accounts.models import User, FriendRequest, Message, UserWallPost, UserWallPostComment
from cricket.models import Cricketer

# local imports
from sportsvitae.shared.factories.account_factories import UserFactory, MidoutUserFactory, FriendRequestFactory, ForeignUserFactory, MessageFactory, UserWallPostFactory,  UserWallImagePostFactory, UserWallLocationPostFactory, UserWallPostCommentFactory
from sportsvitae.shared.factories.cricket_factories import CricketerFactory


@pytest.mark.django_db
class TestUserFactory(unittest.TestCase):

    def setUp(self):
        self.user = UserFactory()

    def test_instantiation(self):
        self.assertTrue(self.user)

    def test_object_created(self):
        self.assertTrue(User.objects.count())

    def test_creates_another_user_with_different_email(self):
        user2 = UserFactory()
        self.assertEqual(User.objects.count(), 2)
        self.assertNotEqual(user2.email, self.user.email)


@pytest.mark.django_db
class TestMidoutUserFactory(unittest.TestCase):

    def setUp(self):
        self.midout_user = MidoutUserFactory()

    def test_instantiation(self):
        self.assertTrue(self.midout_user)

    def test_object_created(self):
        self.assertTrue(User.objects.count())

    def test_creates_another_user_with_different_email(self):
        midout_user2 = MidoutUserFactory()
        self.assertEqual(User.objects.count(), 2)
        self.assertNotEqual(midout_user2.email, self.midout_user.email)


@pytest.mark.django_db
class TestForeignUserFactory(unittest.TestCase):

    def setUp(self):
        self.international_user = ForeignUserFactory()

    def test_instantiation(self):
        self.assertTrue(self.international_user)

    def test_object_created(self):
        self.assertTrue(User.objects.count())

    def test_creates_another_user_with_different_email(self):
        international_user2 = UserFactory()
        self.assertEqual(User.objects.count(), 2)
        self.assertNotEqual(international_user2.email, self.international_user.email)


@pytest.mark.django_db
class TestFriendRequestFactory(unittest.TestCase):

    def setUp(self):
        self.friend_request = FriendRequestFactory()

    def test_instantiation(self):
        self.assertTrue(self.friend_request)

    def test_object_created(self):
        self.assertTrue(FriendRequest.objects.count())

    def test_2_different_users_created(self):
        self.assertEqual(User.objects.all().count(), 2)
        self.assertNotEqual(self.friend_request.to_user, self.friend_request.from_user)

    def test_2_cricketers_created(self):
        self.assertEqual(Cricketer.objects.all().count(), 2)


@pytest.mark.django_db
class TestMessageFactory(unittest.TestCase):

    def setUp(self):
        self.message = MessageFactory()

    def test_instantiation(self):
        self.assertTrue(self.message)

    def test_object_created(self):
        self.assertTrue(Message.objects.count())

    def test_2_different_users_created(self):
        self.assertEqual(User.objects.all().count(), 2)
        self.assertNotEqual(self.message.sender, self.message.recipient)

    def test_2_cricketers_created(self):
        self.assertEqual(Cricketer.objects.all().count(), 2)


@pytest.mark.django_db
class TestUserWallPostFactory(unittest.TestCase):

    def setUp(self):
        self.cricketer = CricketerFactory()
        self.user_wall_post = UserWallPostFactory(cricketer=self.cricketer)
        self.owner = self.user_wall_post.owner

    def test_instantiation(self):
        self.assertTrue(self.user_wall_post)

    def test_object_created(self):
        self.assertTrue(UserWallPost.objects.count())

    def test_user_created(self):
        self.assertTrue(self.owner)
        self.assertEqual(User.objects.all().count(), 1)

    def test_likes_saved_correctly(self):
        self.assertFalse(self.user_wall_post.likes.count())
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        self.owner.add_friend(friend1)
        self.owner.add_friend(friend2)
        post2 = UserWallPostFactory(cricketer=self.cricketer, likes=[friend1, friend2])
        self.assertEqual(post2.likes.count(), 2)
        self.assertTrue(post2.likes.filter(id=friend1.id).exists())
        self.assertTrue(post2.likes.filter(id=friend2.id).exists())

    def test_location_is_none(self):
        self.assertIsNone(self.user_wall_post.location)

    def test_image_is_none(self):
        self.assertRaises(ValueError, getattr, self.user_wall_post.post_image, 'file')


@pytest.mark.django_db
class TestUserWallImagePostFactory(unittest.TestCase):

    def setUp(self):
        self.cricketer = CricketerFactory()
        self.user_wall_image_post = UserWallImagePostFactory(cricketer=self.cricketer)
        self.owner = self.user_wall_image_post.owner

    def test_instantiation(self):
        self.assertTrue(self.user_wall_image_post)

    def test_object_created(self):
        self.assertTrue(UserWallPost.objects.count())

    def test_user_created(self):
        self.assertEqual(User.objects.all().count(), 1)

    def test_likes_saved_correctly(self):
        self.assertFalse(self.user_wall_image_post.likes.count())
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        self.owner.add_friend(friend1)
        self.owner.add_friend(friend2)
        post2 = UserWallPostFactory(cricketer=self.cricketer, likes=[friend1, friend2])
        self.assertEqual(post2.likes.count(), 2)
        self.assertTrue(post2.likes.filter(id=friend1.id).exists())
        self.assertTrue(post2.likes.filter(id=friend2.id).exists())

    def test_text_saved_correctly(self):
        self.assertEqual(self.user_wall_image_post.text, 'Check out this new pic')

    def test_post_type_saved_correctly(self):
        self.assertEqual(self.user_wall_image_post.post_type, 2)

    def test_post_image_saved_correctly(self):
        self.assertIsNotNone(self.user_wall_image_post.post_image.file)
        user_wall_post_image_path = self.user_wall_image_post.post_image.path
        self.assertTrue(os.path.exists(user_wall_post_image_path))

    def test_location_is_none(self):
        self.assertIsNone(self.user_wall_image_post.location)


@pytest.mark.django_db
class TestUserWallLocationPostFactory(unittest.TestCase):

    def setUp(self):
        self.cricketer = CricketerFactory()
        self.user_wall_location_post = UserWallLocationPostFactory(cricketer=self.cricketer)
        self.owner = self.user_wall_location_post.owner

    def test_instantiation(self):
        self.assertTrue(self.user_wall_location_post)

    def test_object_created(self):
        self.assertTrue(UserWallPost.objects.count())

    def test_user_created(self):
        self.assertEqual(User.objects.all().count(), 1)

    def test_likes_saved_correctly(self):
        self.assertFalse(self.user_wall_location_post.likes.count())
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        self.owner.add_friend(friend1)
        self.owner.add_friend(friend2)
        post2 = UserWallPostFactory(cricketer=self.cricketer, likes=[friend1, friend2])
        self.assertEqual(post2.likes.count(), 2)
        self.assertTrue(post2.likes.filter(id=friend1.id).exists())
        self.assertTrue(post2.likes.filter(id=friend2.id).exists())

    def test_text_saved_correctly(self):
        self.assertEqual(self.user_wall_location_post.text, 'Checked in at')

    def test_post_type_saved_correctly(self):
        self.assertEqual(self.user_wall_location_post.post_type, 3)

    def test_location_saved_correctly(self):
        self.assertEqual(self.user_wall_location_post.location, 'Delhi, India')

    def test_image_is_none(self):
        self.assertRaises(ValueError, getattr, self.user_wall_location_post.post_image, 'file')


@pytest.mark.django_db
class TestUserWallPostCommentFactory(unittest.TestCase):

    def setUp(self):
        self.user_wall_post_comment = UserWallPostCommentFactory()
        self.comment_by = self.user_wall_post_comment.comment_by
        self.user_wall_post = self.user_wall_post_comment.user_wall_post
        self.owner = self.user_wall_post.owner

    def test_instantiation(self):
        self.assertTrue(self.user_wall_post_comment)

    def test_object_created(self):
        self.assertTrue(UserWallPostComment.objects.count())

    def test_users_created(self):
        self.assertTrue(self.owner)
        self.assertTrue(self.comment_by)
        self.assertNotEqual(self.owner, self.comment_by)

    def test_user_wall_post_created(self):
        self.assertTrue(self.user_wall_post)
        self.assertEqual(UserWallPost.objects.all().count(), 1)

    def test_likes_saved_correctly(self):
        self.assertFalse(self.user_wall_post_comment.likes.count())
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        self.owner.add_friend(friend1)
        self.owner.add_friend(friend2)
        post_comment2 = UserWallPostCommentFactory(likes=[friend1, friend2])
        self.assertEqual(post_comment2.likes.count(), 2)
        self.assertTrue(post_comment2.likes.filter(id=friend1.id).exists())
        self.assertTrue(post_comment2.likes.filter(id=friend2.id).exists())

    def test_non_friend_user_can_comment(self):
        self.assertFalse(self.owner.friends.filter(id=self.comment_by.id).exists())

    def test_friend_user_can_comment(self):
        friend1 = CricketerFactory().user
        self.owner.add_friend(friend1)
        user_wall_post = UserWallPostFactory(owner=self.owner)
        post_comment = UserWallPostCommentFactory(comment_by=friend1, user_wall_post=user_wall_post)
        self.assertTrue(post_comment)
        self.assertFalse(self.owner.friends.filter(id=self.comment_by.id).exists())

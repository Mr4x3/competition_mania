# Python Imports
import unittest

# Django Imports
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile

# Third Party Django Imports
import pytest

# Inter App Imports
from sportsvitae.shared.factories import UserFactory, MidoutUserFactory, CricketerFactory, FriendRequestFactory, UserWallPostFactory, UserWallPostCommentFactory
from accounts.models import FriendRequest, Message

# Local Imports
from ..serializers import FriendRequestSerializer, UnfriendUserSerializer, SendMessageSerializer, ForgotPasswordSerializer, UserWallPostSerializer, UserWallPostCommentSerializer


@pytest.mark.django_db
class TestFriendRequestSerializer(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.cricketer1 = CricketerFactory()
        self.cricketer2 = CricketerFactory()
        self.user1 = self.cricketer1.user
        self.user2 = self.cricketer2.user
        self.form_data = {
            'from_user': self.user1.id,
            'to_user': self.user2.id
        }
        self.friend_request_serializer = FriendRequestSerializer(data=self.form_data)

    def test_instantiation(self):
        self.assertTrue(self.friend_request_serializer)

    def test_serializer_valid(self):
        self.assertTrue(self.friend_request_serializer.is_valid())

    def test_create_friend_request_on_save(self):
        self.assertEqual(FriendRequest.objects.count(), 0)
        self.friend_request_serializer.is_valid()
        self.friend_request_serializer.save()
        self.assertEqual(FriendRequest.objects.count(), 1)

    def test_returns_error_on_invalid_id(self):
        self.form_data['from_user'] = 'dummy'
        friend_request_serializer = FriendRequestSerializer(data=self.form_data)
        self.assertFalse(friend_request_serializer.is_valid())
        self.assertIn('from_user', friend_request_serializer.errors)

    def test_returns_error_on_non_existent_id(self):
        self.form_data['from_user'] = 999
        friend_request_serializer = FriendRequestSerializer(data=self.form_data)
        self.assertFalse(friend_request_serializer.is_valid())
        self.assertIn('from_user', friend_request_serializer.errors)

    def test_returns_no_error_on_valid_id_in_string(self):
        self.form_data['from_user'] = str(self.user1.id)
        friend_request_serializer = FriendRequestSerializer(data=self.form_data)
        self.assertTrue(friend_request_serializer.is_valid())

    def test_returns_error_if_friend_request_already_exists(self):
        FriendRequestFactory(from_user=self.user1, to_user=self.user2)
        self.assertEqual(FriendRequest.objects.count(), 1)
        self.assertFalse(self.friend_request_serializer.is_valid())
        self.assertIn('non_field_errors', self.friend_request_serializer.errors)
        self.assertNotIn('The fields from_user, to_user must make a unique set.', self.friend_request_serializer.errors['non_field_errors'])
        self.assertIn('Friend request already sent to this user.', self.friend_request_serializer.errors['non_field_errors'])

    def test_returns_error_if_from_user_and_to_user_same(self):
        self.form_data['to_user'] = self.form_data['from_user']
        friend_request_serializer = FriendRequestSerializer(data=self.form_data)
        self.assertFalse(friend_request_serializer.is_valid())

    def test_from_user_cannot_be_empty(self):
        del self.form_data['from_user']
        friend_request_serializer = FriendRequestSerializer(data=self.form_data)
        self.assertFalse(friend_request_serializer.is_valid())
        self.assertIn('from_user', friend_request_serializer.errors)

    def test_from_user_cannot_be_empty(self):
        del self.form_data['to_user']
        friend_request_serializer = FriendRequestSerializer(data=self.form_data)
        self.assertFalse(friend_request_serializer.is_valid())
        self.assertIn('to_user', friend_request_serializer.errors)

    def test_returns_error_if_already_friends(self):
        self.user1.add_friend(self.user2)
        self.assertTrue(self.user1.friends.filter(id=self.user2.id).exists())
        self.assertFalse(self.friend_request_serializer.is_valid())

    def test_returns_error_if_from_user_midout(self):
        midout_user = MidoutUserFactory()
        self.form_data['from_user'] = midout_user.id
        self.assertFalse(midout_user.is_complete_user())
        friend_request_serializer = FriendRequestSerializer(data=self.form_data)
        self.assertFalse(friend_request_serializer.is_valid())
        self.assertIn('from_user', friend_request_serializer.errors)

    def test_returns_error_if_from_user_has_no_sports_profile(self):
        user = UserFactory()
        self.form_data['from_user'] = user.id
        self.assertFalse(user.is_complete_user())
        friend_request_serializer = FriendRequestSerializer(data=self.form_data)
        self.assertFalse(friend_request_serializer.is_valid())
        self.assertIn('from_user', friend_request_serializer.errors)

    def test_returns_error_if_to_user_midout(self):
        midout_user = MidoutUserFactory()
        self.form_data['to_user'] = midout_user.id
        self.assertFalse(midout_user.is_complete_user())
        friend_request_serializer = FriendRequestSerializer(data=self.form_data)
        self.assertFalse(friend_request_serializer.is_valid())
        self.assertIn('to_user', friend_request_serializer.errors)

    def test_returns_error_if_to_user_has_no_sports_profile(self):
        user = UserFactory()
        self.form_data['to_user'] = user.id
        self.assertFalse(user.is_complete_user())
        friend_request_serializer = FriendRequestSerializer(data=self.form_data)
        self.assertFalse(friend_request_serializer.is_valid())
        self.assertIn('to_user', friend_request_serializer.errors)


@pytest.mark.django_db
class TestUnfriendUserSerializer(unittest.TestCase):

    def setUp(self):
        self.user1 = UserFactory()
        self.user2 = UserFactory()
        self.form_data = {
            'friend_id': self.user1.id,
        }
        self.unfriend_user_serializer = UnfriendUserSerializer(data=self.form_data)

    def test_instantiation(self):
        self.assertTrue(self.unfriend_user_serializer)

    def test_serializer_valid(self):
        self.assertTrue(self.unfriend_user_serializer.is_valid())

    def test_serializer_invalid_for_non_integer_value(self):
        self.form_data['friend_id'] = 'dummy'
        unfriend_user_serializer = UnfriendUserSerializer(data=self.form_data)
        self.assertFalse(unfriend_user_serializer.is_valid())

    def test_serializer_invalid_for_non_existing_user_id_value(self):
        self.form_data['friend_id'] = 999
        unfriend_user_serializer = UnfriendUserSerializer(data=self.form_data)
        self.assertFalse(unfriend_user_serializer.is_valid())

    def test_serializer_invalid_if_no_friend_id(self):
        del self.form_data['friend_id']
        unfriend_user_serializer = UnfriendUserSerializer(data=self.form_data)
        self.assertFalse(unfriend_user_serializer.is_valid())

    def test_serializer_if_valid_friend_id_in_string(self):
        self.form_data['friend_id'] = str(self.user1.id)
        unfriend_user_serializer = UnfriendUserSerializer(data=self.form_data)
        self.assertTrue(unfriend_user_serializer.is_valid())


@pytest.mark.django_db
class TestSendMessageSerializer(unittest.TestCase):

    def setUp(self):
        self.sender = CricketerFactory().user
        self.recipient = CricketerFactory().user
        self.sender.add_friend(self.recipient)
        self.form_data = {
            'sender' : self.sender.id,
            'recipient' : self.recipient.id,
            'text': 'Hello'
        }
        self.send_message_serializer = SendMessageSerializer(data=self.form_data)

    def test_instantiation(self):
        self.assertTrue(self.send_message_serializer)

    def test_serializer_valid(self):
        self.assertTrue(self.send_message_serializer.is_valid())

    def test_message_saved(self):
        self.assertTrue(self.send_message_serializer.is_valid())
        self.send_message_serializer.save()
        self.assertEqual(Message.objects.count(), 1)

    def test_user_saved_correctly(self):
        self.send_message_serializer.is_valid()
        message = self.send_message_serializer.save()
        self.assertEqual(message.sender, self.sender)
        self.assertEqual(message.recipient, self.recipient)
        self.assertEqual(message.text, self.form_data['text'])

    def test_invalid_if_sender_missing(self):
        del self.form_data['sender']
        send_message_serializer = SendMessageSerializer(data=self.form_data)
        self.assertFalse(send_message_serializer.is_valid())
        self.assertIn('sender', send_message_serializer.errors)
        self.assertIn('This field is required.', send_message_serializer.errors['sender'])

    def test_invalid_if_recipient_missing(self):
        del self.form_data['recipient']
        send_message_serializer = SendMessageSerializer(data=self.form_data)
        self.assertFalse(send_message_serializer.is_valid())
        self.assertIn('recipient', send_message_serializer.errors)
        self.assertIn('This field is required.', send_message_serializer.errors['recipient'])

    def test_invalid_if_text_missing(self):
        del self.form_data['text']
        send_message_serializer = SendMessageSerializer(data=self.form_data)
        self.assertFalse(send_message_serializer.is_valid())
        self.assertIn('text', send_message_serializer.errors)
        self.assertIn('This field is required.', send_message_serializer.errors['text'])

    def test_returns_error_if_sender_and_recipient_same(self):
        self.form_data['recipient'] = self.form_data['sender']
        send_message_serializer = SendMessageSerializer(data=self.form_data)
        self.assertFalse(send_message_serializer.is_valid())

    def test_returns_error_on_invalid_id(self):
        self.form_data['sender'] = 'dummy'
        send_message_serializer = SendMessageSerializer(data=self.form_data)
        self.assertFalse(send_message_serializer.is_valid())
        self.assertIn('sender', send_message_serializer.errors)

    def test_returns_error_on_non_existent_id(self):
        self.form_data['sender'] = 999
        send_message_serializer = SendMessageSerializer(data=self.form_data)
        self.assertFalse(send_message_serializer.is_valid())
        self.assertIn('sender', send_message_serializer.errors)

    def test_returns_no_error_on_valid_id_in_string(self):
        self.form_data['sender'] = str(self.sender.id)
        send_message_serializer = SendMessageSerializer(data=self.form_data)
        self.assertTrue(send_message_serializer.is_valid())

    def test_returns_error_if_sender_midout(self):
        midout_user = MidoutUserFactory()
        self.form_data['sender'] = midout_user.id
        self.assertFalse(midout_user.is_complete_user())
        send_message_serializer = SendMessageSerializer(data=self.form_data)
        self.assertFalse(send_message_serializer.is_valid())
        self.assertIn('sender', send_message_serializer.errors)

    def test_returns_error_if_sender_has_no_sports_profile(self):
        user = UserFactory()
        self.form_data['sender'] = user.id
        self.assertFalse(user.is_complete_user())
        send_message_serializer = SendMessageSerializer(data=self.form_data)
        self.assertFalse(send_message_serializer.is_valid())
        self.assertIn('sender', send_message_serializer.errors)

    def test_returns_error_if_recipient_midout(self):
        midout_user = MidoutUserFactory()
        self.form_data['recipient'] = midout_user.id
        self.assertFalse(midout_user.is_complete_user())
        send_message_serializer = SendMessageSerializer(data=self.form_data)
        self.assertFalse(send_message_serializer.is_valid())
        self.assertIn('recipient', send_message_serializer.errors)

    def test_returns_error_if_recipient_has_no_sports_profile(self):
        user = UserFactory()
        self.form_data['recipient'] = user.id
        self.assertFalse(user.is_complete_user())
        send_message_serializer = SendMessageSerializer(data=self.form_data)
        self.assertFalse(send_message_serializer.is_valid())
        self.assertIn('recipient', send_message_serializer.errors)

    def test_returns_no_error_if_recipient_is_not_friend_with_sender(self):
        self.sender.friends.clear()
        send_message_serializer = SendMessageSerializer(data=self.form_data)
        self.assertTrue(send_message_serializer.is_valid())


@pytest.mark.django_db
class TestForgotPasswordSerializer(unittest.TestCase):

    def setUp(self):
        self.user = UserFactory()
        self.form_data = {
            'email' : self.user.email
        }
        self.forgot_password_serializer = ForgotPasswordSerializer(data=self.form_data)

    def test_instantiation(self):
        self.assertTrue(self.forgot_password_serializer)

    def test_serializer_valid(self):
        self.assertTrue(self.forgot_password_serializer.is_valid())

    def test_serializer_invalid_for_non_existent_email(self):
        self.form_data['email'] = 'dummy@dummy.com'
        forgot_password_serializer = ForgotPasswordSerializer(data=self.form_data)
        self.assertFalse(forgot_password_serializer.is_valid())
        self.assertIn('email', forgot_password_serializer.errors)


@pytest.mark.django_db
class TestUserWallPostSerializer(unittest.TestCase):

    def setUp(self):
        self.owner = CricketerFactory().user

        self.user_wall_post_picture_path = 'accounts/api/v1/tests/test_user_wall_post_image.jpg'
        self.user_wall_post_picture = SimpleUploadedFile(name='test_user_wall_post_image.png', content=open(self.user_wall_post_picture_path, 'rb').read())

        self.form_data = {
            'text': 'some post',
            'post_type': 1
        }

        self.form_data_image = {
            'text': 'some post',
            'post_image': self.user_wall_post_picture,
            'post_type': 2
        }

        self.form_data_location = {
            'text': 'checked in at',
            'location': 'Delhi',
            'post_type': 3
        }
        self.user_wall_post_serializer = UserWallPostSerializer(data=self.form_data)

    def test_instantiation(self):
        self.assertTrue(self.user_wall_post_serializer)

    def test_serializer_valid(self):
        self.assertTrue(self.user_wall_post_serializer.is_valid())

    def test_serializer_invalid_if_post_type_invalid(self):
        self.form_data['post_image'] = 12
        user_wall_post_serializer = UserWallPostSerializer(data=self.form_data)
        self.assertFalse(user_wall_post_serializer.is_valid())
        self.assertIn('post_image', user_wall_post_serializer.errors)

    def test_serializer_invalid_if_text_missing_for_normal_post(self):
        del self.form_data['text']
        user_wall_post_serializer = UserWallPostSerializer(data=self.form_data)
        self.assertFalse(user_wall_post_serializer.is_valid())
        self.assertIn('non_field_errors', user_wall_post_serializer.errors)
        self.assertIn('Please enter some text.', user_wall_post_serializer.errors['non_field_errors'])

    def test_serializer_returns_no_error_if_post_type_missing(self):
        del self.form_data['post_type']
        user_wall_post_serializer = UserWallPostSerializer(data=self.form_data)
        self.assertTrue(user_wall_post_serializer.is_valid())

    def test_serializer_returns_error_if_no_image_in_image_post(self):
        del self.form_data_image['post_image']
        user_wall_post_serializer = UserWallPostSerializer(data=self.form_data_image)
        self.assertFalse(user_wall_post_serializer.is_valid())
        self.assertIn('non_field_errors', user_wall_post_serializer.errors)
        self.assertIn('Please upload a image.', user_wall_post_serializer.errors['non_field_errors'])

    def test_serializer_returns_no_error_if_no_text_in_image_post(self):
        del self.form_data_image['text']
        user_wall_post_serializer = UserWallPostSerializer(data=self.form_data_image)
        self.assertTrue(user_wall_post_serializer.is_valid())

    def test_serializer_returns_error_if_no_location_in_location_post(self):
        del self.form_data_location['location']
        user_wall_post_serializer = UserWallPostSerializer(data=self.form_data_location)
        self.assertFalse(user_wall_post_serializer.is_valid())
        self.assertIn('non_field_errors', user_wall_post_serializer.errors)
        self.assertIn('Please enter a location.', user_wall_post_serializer.errors['non_field_errors'])

    def test_serializer_returns_no_error_if_no_text_in_location_post(self):
        del self.form_data_location['text']
        user_wall_post_serializer = UserWallPostSerializer(data=self.form_data_location)
        self.assertTrue(user_wall_post_serializer.is_valid())

    def test_location_and_image_set_to_none_if_normal_wall_post(self):
        self.form_data['location'] = self.form_data_location['location']
        self.form_data['post_image'] = self.form_data_image['post_image']
        user_wall_post_serializer = UserWallPostSerializer(data=self.form_data)
        self.assertTrue(user_wall_post_serializer.is_valid())
        self.assertEqual(user_wall_post_serializer.validated_data['location'], None)
        self.assertEqual(user_wall_post_serializer.validated_data['post_image'], None)

    def test_location_set_to_none_if_image_post(self):
        self.form_data_image['location'] = self.form_data_location['location']
        user_wall_post_serializer = UserWallPostSerializer(data=self.form_data_image)
        self.assertTrue(user_wall_post_serializer.is_valid())
        self.assertEqual(user_wall_post_serializer.validated_data['location'], None)

    def test_image_set_to_none_if_location_post(self):
        self.form_data_location['post_image'] = self.form_data_image['post_image']
        user_wall_post_serializer = UserWallPostSerializer(data=self.form_data_location)
        self.assertTrue(user_wall_post_serializer.is_valid())
        self.assertEqual(user_wall_post_serializer.validated_data['post_image'], None)


@pytest.mark.django_db
class TestUserWallPostCommentSerializer(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.cricketer = CricketerFactory()
        self.owner = self.cricketer.user
        self.user_wall_post = UserWallPostFactory(cricketer=self.cricketer)

        self.user_wall_post_comment = UserWallPostCommentFactory(user_wall_post=self.user_wall_post)
        self.comment_by = self.user_wall_post_comment.comment_by
        self.user3 = CricketerFactory().user
        self.user4 = CricketerFactory().user
        self.user_wall_post_comment.likes.add(self.user3)
        self.user_wall_post_comment.likes.add(self.user4)

        self.form_data = {
            'comment' : 'nice post'
        }
        self.user_wall_post_comment_serializer = UserWallPostCommentSerializer(data=self.form_data)

    def test_instantiation(self):
        self.assertTrue(self.user_wall_post_comment_serializer)

    def test_serializer_valid(self):
        self.assertTrue(self.user_wall_post_comment_serializer.is_valid())

    def test_serializer_invalid_for_non_existent_email(self):
        del self.form_data['comment']
        user_wall_post_comment_serializer = UserWallPostCommentSerializer(data=self.form_data)
        self.assertFalse(user_wall_post_comment_serializer.is_valid())
        self.assertIn('comment', user_wall_post_comment_serializer.errors)
        self.assertIn('This field is required.', user_wall_post_comment_serializer.errors['comment'])

    def test_returns_expected_keys_in_serialized_output(self):
        expected_keys = ['id', 'comment', 'user_wall_post', 'commented_on', 'likes', 'comment_by_user_id', 'comment_by_user_name', 'comment_by_user_display_picture']
        comment_serializer = UserWallPostCommentSerializer(self.user_wall_post_comment)
        for key in expected_keys:
            self.assertIn(key, comment_serializer.data)

    def test_returns_user_wall_post_id_in_response(self):
        comment_serializer = UserWallPostCommentSerializer(self.user_wall_post_comment)
        self.assertEqual(comment_serializer.data['user_wall_post'], self.user_wall_post.id)

    def test_returns_comment_by_id_in_response(self):
        comment_serializer = UserWallPostCommentSerializer(self.user_wall_post_comment)
        self.assertEqual(comment_serializer.data['comment_by_user_id'], self.user_wall_post_comment.comment_by.id)

    def test_returns_like_ids_in_response(self):
        comment_serializer = UserWallPostCommentSerializer(self.user_wall_post_comment)
        self.assertEqual(comment_serializer.data['likes'], [self.user3.id, self.user4.id])

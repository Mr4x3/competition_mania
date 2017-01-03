# inbuilt python imports
import unittest
import json
import os

# inbuilt django imports
from django.test import Client
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import Q

# third-party django imports
import pytest
import fudge
from rest_framework import status

# inter-app imports
from sportsvitae.shared.factories import UserFactory, MidoutUserFactory, CricketerFactory, FriendRequestFactory, MessageFactory, UserWallPostFactory, UserWallPostCommentFactory

# local imports
from accounts.models import FriendRequest, Message, UserWallPost, UserWallPostComment, UserNotification


@pytest.mark.django_db
class TestSendFriendRequest(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.cricketer1 = CricketerFactory()
        self.cricketer2 = CricketerFactory()
        self.user1 = self.cricketer1.user
        self.user2 = self.cricketer2.user
        self.client.login(username=self.user1.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('send_friend_request')
        self.post_data = {
            'from_user': self.user1.id,
            'to_user': self.user2.id
        }
        self.response = self.client.post(self.url, self.post_data)

    def test_returns_201_response(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_returns_proper_keys_in_response(self):
        expected_keys = ['id', 'from_user', 'to_user']
        for key in expected_keys:
            self.assertIn(key, self.response.data)

    def test_creates_friend_request_object(self):
        self.assertEqual(FriendRequest.objects.count(), 1)

    def test_correct_from_user(self):
        friend_request = FriendRequest.objects.all()[0]
        self.assertEqual(friend_request.from_user, self.user1)

    def test_correct_to_user(self):
        friend_request = FriendRequest.objects.all()[0]
        self.assertEqual(friend_request.to_user, self.user2)

    def test_accepted_set_to_false(self):
        friend_request = FriendRequest.objects.all()[0]
        self.assertFalse(friend_request.accepted)

    def test_viewed_set_to_false(self):
        friend_request = FriendRequest.objects.all()[0]
        self.assertFalse(friend_request.viewed)

    def test_sent_on_field_set(self):
        friend_request = FriendRequest.objects.all()[0]
        self.assertTrue(friend_request.sent_on)

    def test_get_method_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_idempotent_operation(self):
        self.assertEqual(FriendRequest.objects.count(), 1)
        response2 = self.client.post(self.url, self.post_data)
        response3 = self.client.post(self.url, self.post_data)
        response4 = self.client.post(self.url, self.post_data)
        self.assertEqual(FriendRequest.objects.count(), 1)

    def test_cannot_create_friend_request_with_same_user(self):
        self.post_data['to_user'] = self.post_data['from_user']
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_403_if_not_loggedin(self):
        FriendRequest.objects.all().delete()
        self.client.session.flush()
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_returns_error_if_from_user_not_the_loggedin_user(self):
        FriendRequest.objects.all().delete()
        self.client.session.flush()
        self.user3 = UserFactory()
        self.client.login(username=self.user3.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('from_user', response.data)

    def test_returns_error_if_from_user_midout(self):
        midout_user = MidoutUserFactory()
        self.post_data['from_user'] = midout_user.id
        self.assertFalse(midout_user.is_complete_user())
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('from_user', response.data)

    def test_returns_error_if_from_user_has_no_sports_profile(self):
        user = UserFactory()
        self.post_data['from_user'] = user.id
        self.assertFalse(user.is_complete_user())
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('from_user', response.data)

    def test_returns_error_if_to_user_midout(self):
        midout_user = MidoutUserFactory()
        self.post_data['to_user'] = midout_user.id
        self.assertFalse(midout_user.is_complete_user())
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('to_user', response.data)

    def test_returns_error_if_to_user_has_no_sports_profile(self):
        user = UserFactory()
        self.post_data['to_user'] = user.id
        self.assertFalse(user.is_complete_user())
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('to_user', response.data)


@pytest.mark.django_db
class TestAcceptFriendRequest(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.friend_request = FriendRequestFactory()
        self.user1 = self.friend_request.from_user
        self.user2 = self.friend_request.to_user
        self.display_picture_path = 'accounts/tests/test_display_pic.png'
        self.display_picture = SimpleUploadedFile(name='test_display_pic.png', content=open(self.display_picture_path, 'rb').read())

        self.user1.display_picture = self.display_picture
        self.user2.display_picture = self.display_picture
        self.user1.save()
        self.user2.save()

        self.client.login(username=self.user2.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('accept_friend_request', kwargs={'id':self.friend_request.id})

    def test_returns_200_response(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)

    def test_friend_added(self):
        self.assertEqual(self.user1.friends.count(), 0)
        response = self.client.post(self.url)
        self.assertEqual(self.user1.friends.count(), 1)
        self.assertTrue(self.user1.friends.filter(id=self.user2.id).exists())

    def test_notification_sent_to_sender_only(self):
        UserNotification.objects.all().delete()
        response = self.client.post(self.url)
        self.assertEqual(UserNotification.objects.count(), 1)
        self.assertTrue(UserNotification.objects.filter(user=self.user1).exists())
        self.assertFalse(UserNotification.objects.filter(user=self.user2).exists())

    def test_notification_saved_correctly(self):
        UserNotification.objects.all().delete()
        response = self.client.post(self.url)
        notification1 = UserNotification.objects.get(user=self.user1)
        self.assertEqual(notification1.notification_type, 1)
        self.assertTrue(notification1.created_on)
        self.assertFalse(notification1.viewed)
        self.assertEqual(notification1.message, 'You and <b>Jon Snow</b> are now friends.')
        self.assertEqual(notification1.click_url, reverse('user_wall', kwargs={'slug':self.user2.slug}))
        self.assertEqual(notification1.display_picture.path, self.user2.display_picture.path)

    def test_notification_image_saved_correctly_if_no_image(self):
        UserNotification.objects.all().delete()
        self.user2.display_picture.delete()
        self.user2.save()
        response = self.client.post(self.url)
        notification1 = UserNotification.objects.get(user=self.user1)
        self.assertRaises(ValueError, getattr, self.user2.display_picture, 'file')
        self.assertRaises(ValueError, getattr, notification1.display_picture, 'file')

    def test_friend_added_reverse_side_also(self):
        self.assertEqual(self.user2.friends.count(), 0)
        response = self.client.post(self.url)
        self.assertEqual(self.user2.friends.count(), 1)
        self.assertTrue(self.user2.friends.filter(id=self.user1.id).exists())

    def test_status_set_to_accepted(self):
        self.assertFalse(self.friend_request.accepted)
        response = self.client.post(self.url)
        friend_request = FriendRequest.objects.get(id=self.friend_request.id)
        self.assertTrue(friend_request.accepted)

    def test_returns_404_on_invalid_id(self):
        url = reverse('accept_friend_request', kwargs={'id':999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'detail': 'Not found.'})

    def test_reverse_request_deleted(self):
        friend_request2 = FriendRequestFactory(from_user=self.user2, to_user=self.user1)
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user2, to_user=self.user1).exists())
        response = self.client.post(self.url)
        self.assertFalse(FriendRequest.objects.filter(from_user=self.user2, to_user=self.user1).exists())

    def test_returns_403_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_returns_error_if_different_user_other_than_to_user_loggedin(self):
        self.client.session.flush()
        self.user3 = UserFactory()
        self.client.login(username=self.user3.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
class TestRejectFriendRequest(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.friend_request = FriendRequestFactory()
        self.user1 = self.friend_request.from_user
        self.user2 = self.friend_request.to_user
        self.client.login(username=self.user2.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('reject_friend_request', kwargs={'id':self.friend_request.id})

    def test_returns_200_response(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)

    def test_request_deleted(self):
        self.assertEqual(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).count(), 1)
        response = self.client.post(self.url)
        self.assertEqual(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).count(), 0)

    def test_request_deleted_reverse_side_also(self):
        friend_request2 = FriendRequestFactory(from_user=self.user2, to_user=self.user1)
        self.assertEqual(FriendRequest.objects.filter(from_user=self.user2, to_user=self.user1).count(), 1)
        response = self.client.post(self.url)
        self.assertEqual(FriendRequest.objects.filter(from_user=self.user2, to_user=self.user1).count(), 0)

    def test_returns_404_on_invalid_id(self):
        url = reverse('reject_friend_request', kwargs={'id':999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'detail': 'Not found.'})

    def test_returns_403_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_returns_error_if_different_user_other_than_to_user_loggedin(self):
        self.client.session.flush()
        self.user3 = UserFactory()
        self.client.login(username=self.user3.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
class TestCancelFriendRequest(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.friend_request = FriendRequestFactory()
        self.user1 = self.friend_request.from_user
        self.user2 = self.friend_request.to_user
        self.client.login(username=self.user1.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('cancel_friend_request', kwargs={'id':self.friend_request.id})

    def test_returns_200_response(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 200)

    def test_request_deleted(self):
        self.assertEqual(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).count(), 1)
        response = self.client.post(self.url)
        self.assertEqual(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).count(), 0)

    def test_returns_404_on_invalid_id(self):
        url = reverse('cancel_friend_request', kwargs={'id':999})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'detail': 'Not found.'})

    def test_returns_403_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_returns_error_if_different_user_other_than_from_user_loggedin(self):
        self.client.session.flush()
        self.user3 = UserFactory()
        self.client.login(username=self.user3.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
class TestUnfriendUser(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.cricketer = CricketerFactory()
        self.user = self.cricketer.user
        self.cricketer2 = CricketerFactory()
        self.friend = self.cricketer2.user
        self.user.add_friend(self.friend)
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('unfriend')
        self.post_data = {
            'friend_id': self.friend.id,
        }

    def test_returns_201_response(self):
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unfriends_friend(self):
        self.assertTrue(self.user.friends.filter(id=self.friend.id).exists())
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(self.user.friends.filter(id=self.friend.id).exists())

    def test_existing_friend_request_deleted(self):
        FriendRequest.objects.create(from_user=self.user, to_user=self.friend, accepted=True)
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user, to_user=self.friend).exists())
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(FriendRequest.objects.filter(from_user=self.user, to_user=self.friend).exists())

    def test_existing_reverse_friend_request_deleted(self):
        FriendRequest.objects.create(from_user=self.friend, to_user=self.user, accepted=True)
        self.assertTrue(FriendRequest.objects.filter(from_user=self.friend, to_user=self.user).exists())
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(FriendRequest.objects.filter(from_user=self.friend, to_user=self.user).exists())

    def test_get_method_not_allowed(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_returns_403_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_returns_error_if_unfriend_oneself(self):
        self.post_data['friend_id'] = self.user.id
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_error_if_unfriend_a_non_friend_user(self):
        self.user.remove_friend(self.friend)
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db
class TestUserMessages(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.sender = CricketerFactory().user
        self.recipient = CricketerFactory().user
        self.sender.add_friend(self.recipient)

        self.post_data = {
            'sender' : self.sender.id,
            'recipient' : self.recipient.id,
            'text': 'Hello'
        }

        self.client.login(username=self.sender.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('user_messages_api')
        self.response = self.client.post(self.url, self.post_data)

    def test_returns_200_response_on_get(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_returns_no_messages_if_no_friend_id_parameter(self):
        message = MessageFactory(sender=self.sender, recipient=self.recipient)
        response = self.client.get(self.url)
        self.assertEqual(response.data, [])

    def test_returns_messages_in_response(self):
        Message.objects.all().delete()
        message = MessageFactory(sender=self.sender, recipient=self.recipient)
        url = reverse('user_messages_api') + '?friend_id={}'.format(self.recipient.id)
        response = self.client.get(url)
        self.assertTrue(response.data)
        self.assertEqual(len(response.data), Message.objects.all().count())

    def test_returns_chat_messages_in_response(self):
        Message.objects.all().delete()
        message1 = MessageFactory(sender=self.sender, recipient=self.recipient)
        message2 = MessageFactory(sender=self.recipient, recipient=self.sender)
        message3 = MessageFactory(sender=self.sender)
        url = reverse('user_messages_api') + '?friend_id={}'.format(self.recipient.id)
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)

    def test_returns_only_sent_chat_messages_not_deleted_by_sender_in_response(self):
        Message.objects.all().delete()
        message1 = MessageFactory(sender=self.sender, recipient=self.recipient, deleted_by_sender=True)
        message2 = MessageFactory(sender=self.recipient, recipient=self.sender)
        message3 = MessageFactory(sender=self.sender, recipient=self.recipient, deleted_by_sender=True)
        message4 = MessageFactory(sender=self.sender, recipient=self.recipient)
        message5 = MessageFactory(sender=self.recipient, recipient=self.sender)
        message6 = MessageFactory(sender=self.sender, recipient=self.recipient)
        url = reverse('user_messages_api') + '?friend_id={}'.format(self.recipient.id)
        response = self.client.get(url)
        self.assertEqual(len(response.data), 4)
        messages_data = response.data
        messages_ids_data = [x['id'] for x in messages_data]
        self.assertNotIn(message1.id, messages_ids_data)
        self.assertIn(message2.id, messages_ids_data)
        self.assertNotIn(message3.id, messages_ids_data)
        self.assertIn(message4.id, messages_ids_data)
        self.assertIn(message5.id, messages_ids_data)
        self.assertIn(message6.id, messages_ids_data)

    def test_returns_sent_chat_messages_in_response_even_if_deleted_by_recipient(self):
        Message.objects.all().delete()
        message1 = MessageFactory(sender=self.sender, recipient=self.recipient, deleted_by_recipient=True)
        message2 = MessageFactory(sender=self.recipient, recipient=self.sender)
        message3 = MessageFactory(sender=self.sender, recipient=self.recipient, deleted_by_recipient=True)
        message4 = MessageFactory(sender=self.sender, recipient=self.recipient)
        message5 = MessageFactory(sender=self.recipient, recipient=self.sender)
        message6 = MessageFactory(sender=self.sender, recipient=self.recipient)
        url = reverse('user_messages_api') + '?friend_id={}'.format(self.recipient.id)
        response = self.client.get(url)
        self.assertEqual(len(response.data), 6)
        messages_data = response.data
        messages_ids_data = [x['id'] for x in messages_data]
        self.assertIn(message1.id, messages_ids_data)
        self.assertIn(message2.id, messages_ids_data)
        self.assertIn(message3.id, messages_ids_data)
        self.assertIn(message4.id, messages_ids_data)
        self.assertIn(message5.id, messages_ids_data)
        self.assertIn(message6.id, messages_ids_data)

    def test_returns_only_received_chat_messages_not_deleted_by_recipient_in_response(self):
        Message.objects.all().delete()
        message1 = MessageFactory(sender=self.sender, recipient=self.recipient)
        message2 = MessageFactory(sender=self.recipient, recipient=self.sender, deleted_by_recipient=True)
        message3 = MessageFactory(sender=self.sender, recipient=self.recipient)
        message4 = MessageFactory(sender=self.sender, recipient=self.recipient)
        message5 = MessageFactory(sender=self.recipient, recipient=self.sender, deleted_by_recipient=True)
        message6 = MessageFactory(sender=self.sender, recipient=self.recipient)
        url = reverse('user_messages_api') + '?friend_id={}'.format(self.recipient.id)
        response = self.client.get(url)
        self.assertEqual(len(response.data), 4)
        messages_data = response.data
        messages_ids_data = [x['id'] for x in messages_data]
        self.assertIn(message1.id, messages_ids_data)
        self.assertNotIn(message2.id, messages_ids_data)
        self.assertIn(message3.id, messages_ids_data)
        self.assertIn(message4.id, messages_ids_data)
        self.assertNotIn(message5.id, messages_ids_data)
        self.assertIn(message6.id, messages_ids_data)

    def test_returns_received_chat_messages_in_response_even_if_deleted_by_sender(self):
        Message.objects.all().delete()
        message1 = MessageFactory(sender=self.sender, recipient=self.recipient)
        message2 = MessageFactory(sender=self.recipient, recipient=self.sender, deleted_by_sender=True)
        message3 = MessageFactory(sender=self.sender, recipient=self.recipient)
        message4 = MessageFactory(sender=self.sender, recipient=self.recipient)
        message5 = MessageFactory(sender=self.recipient, recipient=self.sender, deleted_by_sender=True)
        message6 = MessageFactory(sender=self.sender, recipient=self.recipient)
        url = reverse('user_messages_api') + '?friend_id={}'.format(self.recipient.id)
        response = self.client.get(url)
        self.assertEqual(len(response.data), 6)
        messages_data = response.data
        messages_ids_data = [x['id'] for x in messages_data]
        self.assertIn(message1.id, messages_ids_data)
        self.assertIn(message2.id, messages_ids_data)
        self.assertIn(message3.id, messages_ids_data)
        self.assertIn(message4.id, messages_ids_data)
        self.assertIn(message5.id, messages_ids_data)
        self.assertIn(message6.id, messages_ids_data)

    def test_returns_sorted_in_ascending_chat_messages_in_response(self):
        Message.objects.all().delete()
        message1 = MessageFactory(sender=self.sender, recipient=self.recipient, text='hello')
        message2 = MessageFactory(sender=self.recipient, recipient=self.sender, text='world')
        url = reverse('user_messages_api') + '?friend_id={}'.format(self.recipient.id)
        response = self.client.get(url)
        self.assertEqual(response.data[0]['text'], message1.text)
        self.assertEqual(response.data[1]['text'], message2.text)

    def test_returns_correct_keys_in_get_response(self):
        Message.objects.all().delete()
        message = MessageFactory(sender=self.sender, recipient=self.recipient)
        url = reverse('user_messages_api') + '?friend_id={}'.format(self.recipient.id)
        expected_keys = ['sender', 'recipient', 'text', 'sent_on', 'id']
        response = self.client.get(url)
        map(lambda key:self.assertIn(key, response.data[0]), expected_keys)

    def test_returns_201_response_on_post(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_creates_message_object(self):
        self.assertEqual(Message.objects.count(), 1)

    def test_correct_sender(self):
        message = Message.objects.all()[0]
        self.assertEqual(message.sender, self.sender)

    def test_correct_recipient(self):
        message = Message.objects.all()[0]
        self.assertEqual(message.recipient, self.recipient)

    def test_correct_text(self):
        message = Message.objects.all()[0]
        self.assertEqual(message.text, self.post_data['text'])

    def test_unread_set_to_true(self):
        message = Message.objects.all()[0]
        self.assertTrue(message.unread)

    def test_cannot_create_send_message_with_same_user(self):
        self.post_data['recipient'] = self.post_data['sender']
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_returns_403_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_returns_error_if_sender_not_the_loggedin_user(self):
        self.client.session.flush()
        self.user3 = CricketerFactory().user
        self.client.login(username=self.user3.email, password=settings.TEST_USER_PASSWORD)
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('sender', response.data)

    def test_returns_no_error_if_recipient_is_not_friend_with_sender(self):
        self.sender.friends.clear()
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


@pytest.mark.django_db
class TestDeleteFriendChatHistory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CricketerFactory().user
        self.friend = CricketerFactory().user
        self.user.add_friend(self.friend)

        self.message1 = MessageFactory(sender=self.friend, recipient=self.user)
        self.message2 = MessageFactory(sender=self.friend, recipient=self.user)
        self.message3 = MessageFactory(sender=self.friend, recipient=self.user)
        self.message4 = MessageFactory(sender=self.friend, recipient=self.user)
        self.message5 = MessageFactory(sender=self.user, recipient=self.friend)
        self.message6 = MessageFactory(sender=self.user, recipient=self.friend)
        self.message7 = MessageFactory(sender=self.user, recipient=self.friend)
        self.message8 = MessageFactory(sender=self.friend, recipient=self.user)

        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('delete_friend_chat_history', kwargs={'id':self.friend.id})

    def test_returns_204_response_on_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 204)

    def test_does_not_delete_chat_history_objects(self):
        self.assertEqual(Message.objects.filter(Q(sender=self.user, recipient=self.friend)|Q(sender=self.friend, recipient=self.user)).count(), 8)
        response = self.client.delete(self.url)
        self.assertEqual(Message.objects.filter(Q(sender=self.user, recipient=self.friend)|Q(sender=self.friend, recipient=self.user)).count(), 8)

    def test_returns_error_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 403)

    def test_returns_404_if_invalid_friend_id(self):
        url = reverse('delete_friend_chat_history', kwargs={'id':999})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 404)

    def test_returns_404_if_valid_friend_id_but_not_friend(self):
        self.user.friends.clear()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 404)

    def test_deleted_by_sender_flag_set_for_sent_messages(self):
        messages = Message.objects.filter(sender=self.user, recipient=self.friend)
        for message in messages:
            self.assertFalse(message.deleted_by_sender)
        response = self.client.delete(self.url)
        updated_messages = Message.objects.filter(sender=self.user, recipient=self.friend)
        for message in updated_messages:
            self.assertTrue(message.deleted_by_sender)

    def test_deleted_by_recipient_flag_set_for_recieved_messages(self):
        messages = Message.objects.filter(sender=self.friend, recipient=self.user)
        for message in messages:
            self.assertFalse(message.deleted_by_recipient)
        response = self.client.delete(self.url)
        updated_messages = Message.objects.filter(sender=self.friend, recipient=self.user)
        for message in updated_messages:
            self.assertTrue(message.deleted_by_recipient)


@pytest.mark.django_db
class TestForgotPassword(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = UserFactory()
        self.url = reverse('forgot_password')
        self.post_data = {
            'email': self.user.email
        }

    def test_returns_200_response(self):
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @fudge.patch('accounts.api.v1.views.send_forgot_password_mail')
    def test_forgot_password_mail_sent(self, mock_send_mail):
        mock_send_mail.expects_call()
        response = self.client.post(self.url, self.post_data)

    def test_returns_error_if_non_existent_email(self):
        self.post_data['email'] = 'dummy@dummy.com'
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)


@pytest.mark.django_db
class TestResendVerificationMail(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = UserFactory(is_email_verified=False)
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('resend_verification_mail')

    def test_returns_200_response(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @fudge.patch('accounts.api.v1.views.send_email_verification_mail')
    def test_email_sent(self, mock_send_mail):
        mock_send_mail.expects_call()
        response = self.client.get(self.url)

    @fudge.patch('accounts.api.v1.views.send_email_verification_mail')
    def test_email_not_sent_if_email_verified(self, mock_send_mail):
        self.user.is_email_verified = True
        self.user.save()
        response = self.client.get(self.url)

    def test_returns_403_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


@pytest.mark.django_db
class TestUserWallPostCreateDestroyViewSet(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.cricketer = CricketerFactory()
        self.owner = self.cricketer.user
        self.user_wall_post = UserWallPostFactory(cricketer=self.cricketer)
        self.client.login(username=self.owner.email, password=settings.TEST_USER_PASSWORD)

        self.user_wall_post_picture_path = 'accounts/api/v1/tests/test_user_wall_post_image.jpg'
        self.user_wall_post_picture = SimpleUploadedFile(name='test_user_wall_post_image.png', content=open(self.user_wall_post_picture_path, 'rb').read())

        self.user_wall_post_comment1 = UserWallPostCommentFactory(user_wall_post=self.user_wall_post)
        self.user_wall_post_comment2 = UserWallPostCommentFactory(user_wall_post=self.user_wall_post)
        self.user_wall_post_comment3 = UserWallPostCommentFactory(user_wall_post=self.user_wall_post)
        self.user4 = CricketerFactory().user
        self.user5 = CricketerFactory().user
        self.user_wall_post_comment1.likes.add(self.user4)
        self.user_wall_post_comment1.likes.add(self.user5)

        self.create_url = reverse('user_wall_post-list')

        self.delete_url = reverse('user_wall_post-detail', kwargs={'pk': str(self.user_wall_post.id)})

        self.like_url_template = '/api/v1/accounts/user-wall-posts/{id}/like/'
        self.like_url = self.like_url_template.format(id=self.user_wall_post.id)

        self.unlike_url_template = '/api/v1/accounts/user-wall-posts/{id}/unlike/'
        self.unlike_url = self.unlike_url_template.format(id=self.user_wall_post.id)

        self.comment_url_template = '/api/v1/accounts/user-wall-posts/{id}/comments/'
        self.comment_url = self.comment_url_template.format(id=self.user_wall_post.id)

        self.post_data = {
            'text': 'some post',
            'post_type': 1
        }

        self.post_data_image = {
            'text': 'some post',
            'post_image': self.user_wall_post_picture,
            'post_type': 2
        }

        self.post_data_location = {
            'text': 'checked in at',
            'location': 'Delhi',
            'post_type': 3
        }

        self.comment_post_data = {
            'comment': 'Nice post'
        }

        self.display_picture_path = 'accounts/tests/test_display_pic.png'

        self.display_picture = SimpleUploadedFile(name='test_display_pic.png', content=open(self.display_picture_path, 'rb').read())
        self.user_wall_post_comment1.comment_by.display_picture = self.display_picture
        self.user_wall_post_comment2.comment_by.display_picture = self.display_picture
        self.user_wall_post_comment3.comment_by.display_picture = self.display_picture

        self.user_wall_post_comment1.comment_by.save()
        self.user_wall_post_comment2.comment_by.save()
        self.user_wall_post_comment3.comment_by.save()

    def test_returns_204_response_on_delete(self):
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 204)

    def test_deletes_wall_post_on_delete(self):
        self.assertTrue(UserWallPost.objects.filter(id=self.user_wall_post.id).exists())
        response = self.client.delete(self.delete_url)
        self.assertFalse(UserWallPost.objects.filter(id=self.user_wall_post.id).exists())

    def test_user_comments_also_deleted_if_post_deleted(self):
        self.assertEqual(UserWallPostComment.objects.count(), 3)
        self.assertTrue(UserWallPostComment.objects.filter(user_wall_post=self.user_wall_post).exists())
        self.assertTrue(UserWallPost.objects.filter(id=self.user_wall_post.id).exists())

        response = self.client.delete(self.delete_url)

        self.assertFalse(UserWallPost.objects.filter(id=self.user_wall_post.id).exists())
        self.assertFalse(UserWallPostComment.objects.filter(user_wall_post=self.user_wall_post).exists())
        self.assertEqual(UserWallPostComment.objects.count(), 0)

    def test_returns_404_response_on_2nd_request_and_so_on(self):
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 204)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 404)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_another_user_wall_post(self):
        cricketer2 = CricketerFactory()
        owner2 = self.cricketer.user
        user_wall_post = UserWallPostFactory(cricketer=cricketer2)
        self.delete_url = reverse('user_wall_post-detail', kwargs={'pk': str(user_wall_post.id)})
        response = self.client.delete(self.delete_url)
        self.assertNotEqual(response.status_code, 204)
        self.assertEqual(response.status_code, 404)

    def test_returns_201_response_on_user_wall_post(self):
        response = self.client.post(self.create_url, self.post_data)
        self.assertEqual(response.status_code, 201)

    def test_returns_correct_keys_on_create_user_wall_post(self):
        expected_keys = ['id', 'text', 'post_image', 'location', 'post_type']
        response = self.client.post(self.create_url, self.post_data)
        for key in expected_keys:
            self.assertIn(key, response.data)

    def test_creates_user_wall_post_successfully(self):
        UserWallPost.objects.all().delete()
        self.assertEqual(UserWallPost.objects.count(), 0)
        response = self.client.post(self.create_url, self.post_data)
        self.assertEqual(UserWallPost.objects.count(), 1)

    def test_creates_user_wall_post_correctly(self):
        UserWallPost.objects.all().delete()
        self.assertEqual(UserWallPost.objects.count(), 0)
        response = self.client.post(self.create_url, self.post_data)
        user_wall_post = UserWallPost.objects.all()[0]
        self.assertEqual(user_wall_post.owner, self.owner)
        self.assertEqual(user_wall_post.text, self.post_data['text'])
        self.assertEqual(user_wall_post.location, None)
        self.assertRaises(ValueError, getattr, user_wall_post.post_image, 'file')
        self.assertEqual(user_wall_post.post_type, self.post_data['post_type'])

    def test_returns_201_response_on_user_wall_image_post(self):
        response = self.client.post(self.create_url, self.post_data_image)
        self.assertEqual(response.status_code, 201)

    def test_creates_user_wall_image_post_successfully(self):
        UserWallPost.objects.all().delete()
        self.assertEqual(UserWallPost.objects.count(), 0)
        response = self.client.post(self.create_url, self.post_data_image)
        self.assertEqual(UserWallPost.objects.count(), 1)

    def test_creates_user_wall_image_post_correctly(self):
        UserWallPost.objects.all().delete()
        response = self.client.post(self.create_url, self.post_data_image)
        user_wall_post = UserWallPost.objects.all()[0]
        self.assertEqual(user_wall_post.owner, self.owner)
        self.assertEqual(user_wall_post.text, self.post_data_image['text'])
        self.assertEqual(user_wall_post.location, None)
        self.assertTrue(user_wall_post.post_image.file.file)
        self.assertEqual(user_wall_post.post_type, self.post_data_image['post_type'])

    def test_user_wall_post_image_uploaded_correctly(self):
        UserWallPost.objects.all().delete()
        response = self.client.post(self.create_url, self.post_data_image)
        user_wall_post = UserWallPost.objects.all()[0]
        user_wall_post_picture_path = user_wall_post.post_image.path
        self.assertTrue(os.path.exists(user_wall_post_picture_path))

    def test_returns_201_response_on_user_wall_location_post(self):
        response = self.client.post(self.create_url, self.post_data_location)
        self.assertEqual(response.status_code, 201)

    def test_creates_user_wall_location_post_successfully(self):
        UserWallPost.objects.all().delete()
        self.assertEqual(UserWallPost.objects.count(), 0)
        response = self.client.post(self.create_url, self.post_data_location)
        self.assertEqual(UserWallPost.objects.count(), 1)

    def test_creates_user_wall_location_post_correctly(self):
        UserWallPost.objects.all().delete()
        self.assertEqual(UserWallPost.objects.count(), 0)
        response = self.client.post(self.create_url, self.post_data_location)
        user_wall_post = UserWallPost.objects.all()[0]
        self.assertEqual(user_wall_post.owner, self.owner)
        self.assertEqual(user_wall_post.text, self.post_data_location['text'])
        self.assertEqual(user_wall_post.location, self.post_data_location['location'])
        self.assertRaises(ValueError, getattr, user_wall_post.post_image, 'file')
        self.assertEqual(user_wall_post.post_type, self.post_data_location['post_type'])

    def test_returns_error_if_text_missing_for_normal_post(self):
        del self.post_data['text']
        response = self.client.post(self.create_url, self.post_data)
        self.assertEqual(response.status_code, 400)
        self.assertIn('non_field_errors', response.data)

    def test_saves_post_type_as_1_if_missing(self):
        del self.post_data['post_type']
        response = self.client.post(self.create_url, self.post_data)
        user_wall_post = UserWallPost.objects.all()[0]
        self.assertEqual(user_wall_post.post_type, 1)

    def test_returns_error_if_no_image_in_image_post(self):
        del self.post_data_image['post_image']
        response = self.client.post(self.create_url, self.post_data_image)
        self.assertEqual(response.status_code, 400)

    def test_returns_no_error_if_no_text_in_image_post(self):
        del self.post_data_image['text']
        response = self.client.post(self.create_url, self.post_data_image)
        self.assertEqual(response.status_code, 201)

    def test_returns_error_if_no_location_in_location_post(self):
        del self.post_data_location['location']
        response = self.client.post(self.create_url, self.post_data_location)
        self.assertEqual(response.status_code, 400)

    def test_returns_no_error_if_no_text_in_location_post(self):
        del self.post_data_location['text']
        response = self.client.post(self.create_url, self.post_data_location)
        self.assertEqual(response.status_code, 201)

    def test_location_and_image_set_to_none_if_normal_wall_post(self):
        UserWallPost.objects.all().delete()
        self.post_data['location'] = self.post_data_location['location']
        self.post_data['post_image'] = self.post_data_image['post_image']
        response = self.client.post(self.create_url, self.post_data)
        user_wall_post = UserWallPost.objects.all()[0]
        self.assertEqual(user_wall_post.location, None)
        self.assertRaises(ValueError, getattr, user_wall_post.post_image, 'file')

    def test_location_set_to_none_if_image_post(self):
        UserWallPost.objects.all().delete()
        self.post_data_image['location'] = self.post_data_location['location']
        response = self.client.post(self.create_url, self.post_data_image)
        user_wall_post = UserWallPost.objects.all()[0]
        self.assertEqual(user_wall_post.location, None)

    def test_image_set_to_none_if_location_post(self):
        UserWallPost.objects.all().delete()
        self.post_data_location['post_image'] = self.post_data_image['post_image']
        response = self.client.post(self.create_url, self.post_data_location)
        user_wall_post = UserWallPost.objects.all()[0]
        self.assertRaises(ValueError, getattr, user_wall_post.post_image, 'file')

    def test_returns_201_response_on_a_user_post_like(self):
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, 201)

    def test_self_like_saved_on_wall_post(self):
        self.assertEqual(self.user_wall_post.likes.count(), 0)
        response = self.client.post(self.like_url)
        self.user_wall_post = UserWallPost.objects.get(id=self.user_wall_post.id)
        self.assertEqual(self.user_wall_post.likes.count(), 1)
        self.assertIn(self.owner, self.user_wall_post.likes.all())

    def test_like_saved_for_non_friend_user(self):
        self.user2 = CricketerFactory().user
        self.assertNotIn(self.user2, self.owner.friends.all())
        self.client.session.flush()
        self.client.login(username=self.user2.email, password=settings.TEST_USER_PASSWORD)
        self.assertEqual(self.user_wall_post.likes.count(), 0)
        response = self.client.post(self.like_url)
        self.user_wall_post = UserWallPost.objects.get(id=self.user_wall_post.id)
        self.assertEqual(self.user_wall_post.likes.count(), 1)
        self.assertIn(self.user2, self.user_wall_post.likes.all())

    def test_like_saved_for_friend_user(self):
        self.user2 = CricketerFactory().user
        self.owner.add_friend(self.user2)
        self.assertIn(self.user2, self.owner.friends.all())
        self.client.session.flush()
        self.client.login(username=self.user2.email, password=settings.TEST_USER_PASSWORD)
        self.assertEqual(self.user_wall_post.likes.count(), 0)
        response = self.client.post(self.like_url)
        self.user_wall_post = UserWallPost.objects.get(id=self.user_wall_post.id)
        self.assertEqual(self.user_wall_post.likes.count(), 1)
        self.assertIn(self.user2, self.user_wall_post.likes.all())

    def test_returns_error_on_like_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, 403)

    def test_get_method_not_allowed_on_likes(self):
        response = self.client.get(self.like_url)
        self.assertEqual(response.status_code, 405)

    def test_like_operation_idempotent(self):
        self.assertEqual(self.user_wall_post.likes.count(), 0)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, 201)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, 201)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, 201)
        self.user_wall_post = UserWallPost.objects.get(id=self.user_wall_post.id)
        self.assertEqual(self.user_wall_post.likes.count(), 1)
        self.assertIn(self.owner, self.user_wall_post.likes.all())

    def test_returns_404_if_like_on_invalid_post(self):
        self.like_url = self.like_url_template.format(id=999)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, 404)

    def test_returns_201_response_on_a_user_post_unlike(self):
        response = self.client.post(self.unlike_url)
        self.assertEqual(response.status_code, 201)

    def test_like_removed_on_wall_post_unlike(self):
        self.user_wall_post.likes.add(self.owner)
        self.assertEqual(self.user_wall_post.likes.count(), 1)
        self.assertIn(self.owner, self.user_wall_post.likes.all())
        response = self.client.post(self.unlike_url)
        self.assertEqual(self.user_wall_post.likes.count(), 0)

    def test_returns_no_error_if_unlike_on_non_liked_wall_post(self):
        self.assertEqual(self.user_wall_post.likes.count(), 0)
        response = self.client.post(self.unlike_url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.user_wall_post.likes.count(), 0)

    def test_returns_error_on_unlike_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.post(self.unlike_url)
        self.assertEqual(response.status_code, 403)

    def test_get_method_not_allowed_on_unlike(self):
        response = self.client.get(self.unlike_url)
        self.assertEqual(response.status_code, 405)

    def test_unlike_operation_idempotent(self):
        self.user_wall_post.likes.add(self.owner)
        self.assertIn(self.owner, self.user_wall_post.likes.all())
        self.assertEqual(self.user_wall_post.likes.count(), 1)
        response = self.client.post(self.unlike_url)
        self.assertEqual(response.status_code, 201)
        response = self.client.post(self.unlike_url)
        self.assertEqual(response.status_code, 201)
        response = self.client.post(self.unlike_url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.user_wall_post.likes.count(), 0)

    def test_returns_404_if_unlike_on_invalid_post(self):
        unlike_url = self.unlike_url_template.format(id=999)
        response = self.client.post(unlike_url)
        self.assertEqual(response.status_code, 404)

    def test_returns_201_response_on_a_user_post_comment(self):
        response = self.client.post(self.comment_url, self.comment_post_data)
        self.assertEqual(response.status_code, 201)

    def test_returns_correct_keys_on_create_user_wall_post_comment(self):
        expected_keys = ['id', 'comment', 'user_wall_post', 'commented_on', 'likes']
        response = self.client.post(self.comment_url, self.comment_post_data)
        for key in expected_keys:
            self.assertIn(key, response.data)

    def test_returns_no_comment_likes_in_create_post_response(self):
        response = self.client.post(self.comment_url, self.comment_post_data)
        likes = response.data['likes']
        self.assertEqual(likes, [])

    def test_comment_saved_on_wall_post(self):
        UserWallPostComment.objects.all().delete()
        response = self.client.post(self.comment_url, self.comment_post_data)
        self.assertEqual(UserWallPostComment.objects.count(), 1)

    def test_self_comment_saved_on_wall_post(self):
        UserWallPostComment.objects.all().delete()
        response = self.client.post(self.comment_url, self.comment_post_data)
        comment = UserWallPostComment.objects.all()[0]
        self.assertEqual(comment.comment_by, self.owner)
        self.assertEqual(comment.user_wall_post, self.user_wall_post)
        self.assertEqual(comment.comment, self.comment_post_data['comment'])
        self.assertTrue(comment.commented_on)
        self.assertEqual(comment.comment_by, self.user_wall_post.owner)

    def test_comment_saved_for_non_friend_user(self):
        UserWallPostComment.objects.all().delete()
        self.user2 = CricketerFactory().user
        self.assertNotIn(self.user2, self.owner.friends.all())
        self.client.session.flush()
        self.client.login(username=self.user2.email, password=settings.TEST_USER_PASSWORD)
        self.assertEqual(self.user_wall_post.user_wall_post_comments.count(), 0)
        response = self.client.post(self.comment_url, self.comment_post_data)
        self.assertEqual(self.user_wall_post.user_wall_post_comments.count(), 1)
        self.user_wall_post_comment = UserWallPostComment.objects.get(user_wall_post=self.user_wall_post)
        self.assertEqual(self.user_wall_post_comment.comment_by, self.user2)
        self.assertIn(self.user_wall_post_comment, self.user_wall_post.user_wall_post_comments.all())

    def test_comment_saved_for_friend_user(self):
        UserWallPostComment.objects.all().delete()
        self.user2 = CricketerFactory().user
        self.owner.add_friend(self.user2)
        self.assertIn(self.user2, self.owner.friends.all())
        self.client.session.flush()
        self.client.login(username=self.user2.email, password=settings.TEST_USER_PASSWORD)
        self.assertEqual(self.user_wall_post.user_wall_post_comments.count(), 0)
        response = self.client.post(self.comment_url, self.comment_post_data)
        self.assertEqual(self.user_wall_post.user_wall_post_comments.count(), 1)
        self.user_wall_post_comment = UserWallPostComment.objects.get(user_wall_post=self.user_wall_post)
        self.assertEqual(self.user_wall_post_comment.comment_by, self.user2)
        self.assertIn(self.user_wall_post_comment, self.user_wall_post.user_wall_post_comments.all())

    def test_returns_error_on_comments_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.post(self.comment_url, self.comment_post_data)
        self.assertEqual(response.status_code, 403)

    def test_returns_404_if_comment_on_invalid_post(self):
        self.comment_url = self.comment_url_template.format(id=999)
        response = self.client.post(self.comment_url, self.comment_post_data)
        self.assertEqual(response.status_code, 404)

    def test_returns_200_response_on_comments_get(self):
        response = self.client.get(self.comment_url)
        self.assertEqual(response.status_code, 200)

    def test_returns_comments_in_get_response(self):
        response = self.client.get(self.comment_url)
        self.assertTrue(response.data)
        self.assertEqual(len(response.data), 3)

    def test_returns_expected_keys_in_response(self):
        expected_keys = ['id', 'comment', 'user_wall_post', 'commented_on', 'likes', 'comment_by_user_name', 'comment_by_user_display_picture']
        response = self.client.get(self.comment_url)
        for comment in response.data:
            for key in expected_keys:
                self.assertIn(key, comment)

    def test_returns_comment_like_ids_in_response(self):
        response = self.client.get(self.comment_url)
        comment = response.data[0]
        self.assertEqual(comment['likes'], [self.user4.id, self.user5.id])

    def test_returns_404_if_get_comment_on_invalid_post(self):
        self.comment_url = self.comment_url_template.format(id=999)
        response = self.client.get(self.comment_url)
        self.assertEqual(response.status_code, 404)

    def test_returns_error_on_get_comments_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.get(self.comment_url)
        self.assertEqual(response.status_code, 403)

    def test_returns_user_name_in_comments_response(self):
        response = self.client.get(self.comment_url)
        self.assertEqual(response.data[0]['comment_by_user_name'], self.user_wall_post_comment1.comment_by.name)
        self.assertEqual(response.data[1]['comment_by_user_name'], self.user_wall_post_comment2.comment_by.name)
        self.assertEqual(response.data[2]['comment_by_user_name'], self.user_wall_post_comment3.comment_by.name)

    def test_returns_user_display_picture_link_in_comments_response(self):
        response = self.client.get(self.comment_url)
        self.assertEqual(response.data[0]['comment_by_user_display_picture'], self.user_wall_post_comment1.comment_by.display_picture.url)
        self.assertEqual(response.data[1]['comment_by_user_display_picture'], self.user_wall_post_comment2.comment_by.display_picture.url)
        self.assertEqual(response.data[2]['comment_by_user_display_picture'], self.user_wall_post_comment3.comment_by.display_picture.url)

    def test_returns_user_display_picture_link_none_in_comments_response_if_no_image(self):
        self.user_wall_post_comment1.comment_by.display_picture = None
        self.user_wall_post_comment2.comment_by.display_picture = None
        self.user_wall_post_comment3.comment_by.display_picture = None

        self.user_wall_post_comment1.comment_by.save()
        self.user_wall_post_comment2.comment_by.save()
        self.user_wall_post_comment3.comment_by.save()

        response = self.client.get(self.comment_url)
        self.assertEqual(response.data[0]['comment_by_user_display_picture'], None)
        self.assertEqual(response.data[1]['comment_by_user_display_picture'], None)
        self.assertEqual(response.data[2]['comment_by_user_display_picture'], None)


@pytest.mark.django_db
class TestUserWallPostCommentLikeView(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user_wall_post_comment = UserWallPostCommentFactory()
        self.owner = self.user_wall_post_comment.user_wall_post.owner
        self.user = self.user_wall_post_comment.comment_by
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)

        self.like_url_template = '/api/v1/accounts/user-wall-post-comments/{id}/like/'
        self.like_url = self.like_url_template.format(id=self.user_wall_post_comment.id)

    def test_returns_201_response_on_a_user_post_like(self):
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, 201)

    def test_self_like_saved_on_wall_post(self):
        self.user_wall_post_comment.user_wall_post.owner = self.user
        self.user_wall_post_comment.user_wall_post.save()
        self.assertEqual(self.user_wall_post_comment.likes.count(), 0)
        response = self.client.post(self.like_url)
        self.user_wall_post_comment = UserWallPostComment.objects.get(id=self.user_wall_post_comment.id)
        self.assertEqual(self.user_wall_post_comment.likes.count(), 1)
        self.assertIn(self.user, self.user_wall_post_comment.likes.all())

    def test_like_saved_for_non_friend_user(self):
        self.user2 = CricketerFactory().user
        self.assertNotIn(self.user2, self.owner.friends.all())
        self.client.session.flush()
        self.client.login(username=self.user2.email, password=settings.TEST_USER_PASSWORD)
        self.assertEqual(self.user_wall_post_comment.likes.count(), 0)
        response = self.client.post(self.like_url)
        self.user_wall_post_comment = UserWallPostComment.objects.get(id=self.user_wall_post_comment.id)
        self.assertEqual(self.user_wall_post_comment.likes.count(), 1)
        self.assertIn(self.user2, self.user_wall_post_comment.likes.all())

    def test_like_saved_for_friend_user(self):
        self.user2 = CricketerFactory().user
        self.owner.add_friend(self.user2)
        self.assertIn(self.user2, self.owner.friends.all())
        self.client.session.flush()
        self.client.login(username=self.user2.email, password=settings.TEST_USER_PASSWORD)
        self.assertEqual(self.user_wall_post_comment.likes.count(), 0)
        response = self.client.post(self.like_url)
        self.user_wall_post_comment = UserWallPostComment.objects.get(id=self.user_wall_post_comment.id)
        self.assertEqual(self.user_wall_post_comment.likes.count(), 1)
        self.assertIn(self.user2, self.user_wall_post_comment.likes.all())

    def test_like_operation_idempotent(self):
        self.assertEqual(self.user_wall_post_comment.likes.count(), 0)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, 201)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, 201)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, 201)
        self.user_wall_post_comment = UserWallPostComment.objects.get(id=self.user_wall_post_comment.id)
        self.assertEqual(self.user_wall_post_comment.likes.count(), 1)
        self.assertIn(self.user, self.user_wall_post_comment.likes.all())

    def test_returns_error_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, 403)

    def test_get_method_not_allowed_on_comments(self):
        response = self.client.get(self.like_url)
        self.assertEqual(response.status_code, 405)

    def test_returns_404_if_comment_on_invalid_post(self):
        self.like_url = self.like_url_template.format(id=999)
        response = self.client.post(self.like_url)
        self.assertEqual(response.status_code, 404)


@pytest.mark.django_db
class TestUserWallPostCommentUnLikeView(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user_wall_post_comment = UserWallPostCommentFactory()
        self.user = self.user_wall_post_comment.user_wall_post.owner
        self.comment_by = self.user_wall_post_comment.comment_by
        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)

        self.unlike_url_template = '/api/v1/accounts/user-wall-post-comments/{id}/unlike/'
        self.unlike_url = self.unlike_url_template.format(id=self.user_wall_post_comment.id)

    def test_returns_201_response_on_a_user_post_comment_unlike(self):
        response = self.client.post(self.unlike_url)
        self.assertEqual(response.status_code, 201)

    def test_returns_error_on_comments_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.post(self.unlike_url)
        self.assertEqual(response.status_code, 403)

    def test_get_method_not_allowed_on_comments(self):
        response = self.client.get(self.unlike_url)
        self.assertEqual(response.status_code, 405)

    def test_returns_404_if_comment_on_invalid_post(self):
        self.unlike_url = self.unlike_url_template.format(id=999)
        response = self.client.post(self.unlike_url)
        self.assertEqual(response.status_code, 404)

    def test_like_removed_on_wall_post_comment_unlike(self):
        self.user_wall_post_comment.likes.add(self.user)
        self.assertEqual(self.user_wall_post_comment.likes.count(), 1)
        self.assertIn(self.user, self.user_wall_post_comment.likes.all())
        response = self.client.post(self.unlike_url)
        self.assertEqual(self.user_wall_post_comment.likes.count(), 0)

    def test_returns_no_error_if_unlike_on_non_liked_wall_post(self):
        self.assertEqual(self.user_wall_post_comment.likes.count(), 0)
        response = self.client.post(self.unlike_url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.user_wall_post_comment.likes.count(), 0)

    def test_unlike_operation_idempotent(self):
        self.user_wall_post_comment.likes.add(self.user)
        self.assertIn(self.user, self.user_wall_post_comment.likes.all())
        self.assertEqual(self.user_wall_post_comment.likes.count(), 1)
        response = self.client.post(self.unlike_url)
        self.assertEqual(response.status_code, 201)
        response = self.client.post(self.unlike_url)
        self.assertEqual(response.status_code, 201)
        response = self.client.post(self.unlike_url)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(self.user_wall_post_comment.likes.count(), 0)


@pytest.mark.django_db
class TestUserWallPostCommentDeleteView(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user_wall_post_comment = UserWallPostCommentFactory()
        self.user = self.user_wall_post_comment.user_wall_post.owner
        self.comment_by = self.user_wall_post_comment.comment_by
        self.client.login(username=self.comment_by.email, password=settings.TEST_USER_PASSWORD)

        self.delete_url_template = '/api/v1/accounts/user-wall-post-comments/{id}/'
        self.delete_url = self.delete_url_template.format(id=self.user_wall_post_comment.id)

    def test_returns_204_response_on_a_user_post_comment_delete(self):
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 204)

    def test_returns_error_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 403)

    def test_get_method_not_allowed_on_comments(self):
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 405)

    def test_returns_404_if_comment_on_invalid_post(self):
        self.delete_url = self.delete_url_template.format(id=999)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 404)

    def test_deletes_wall_post_on_delete(self):
        self.assertTrue(UserWallPostComment.objects.filter(id=self.user_wall_post_comment.id).exists())
        response = self.client.delete(self.delete_url)
        self.assertFalse(UserWallPostComment.objects.filter(id=self.user_wall_post_comment.id).exists())

    def test_returns_404_response_on_2nd_request_and_so_on(self):
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 204)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 404)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, 404)

    def test_cannot_delete_another_user_wall_post(self):
        cricketer2 = CricketerFactory()
        owner2 = cricketer2.user
        user_wall_post_comment = UserWallPostCommentFactory(cricketer=cricketer2)
        self.delete_url = self.delete_url_template.format(id=user_wall_post_comment.id)
        response = self.client.delete(self.delete_url)
        self.assertNotEqual(response.status_code, 204)
        self.assertEqual(response.status_code, 404)


@pytest.mark.django_db
class TestMarkUserMessagesRead(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CricketerFactory().user
        self.sender1 = CricketerFactory().user
        self.sender2 = CricketerFactory().user
        self.sender3 = CricketerFactory().user
        self.sender4 = CricketerFactory().user
        self.user.add_friend(self.sender1)
        self.user.add_friend(self.sender2)
        self.user.add_friend(self.sender3)
        self.user.add_friend(self.sender4)

        self.message1 = MessageFactory(sender=self.sender1, recipient=self.user)
        self.message2 = MessageFactory(sender=self.sender1, recipient=self.user)
        self.message3 = MessageFactory(sender=self.sender2, recipient=self.user)
        self.message4 = MessageFactory(sender=self.sender2, recipient=self.user)
        self.message5 = MessageFactory(sender=self.sender3, recipient=self.user)
        self.message6 = MessageFactory(sender=self.sender3, recipient=self.user)
        self.message7 = MessageFactory(sender=self.sender4, recipient=self.user)
        self.message8 = MessageFactory(sender=self.sender4, recipient=self.user)

        self.post_data = {
            'message_sender_ids[]' : [x.sender.id for x in self.user.get_latest_received_messages()]
        }

        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('mark_user_messages_viewed')

    def test_returns_201_response_on_post(self):
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_marks_latest_message_as_viewed(self):
        self.assertTrue(self.message4.unread)
        self.assertTrue(self.message6.unread)
        self.assertTrue(self.message8.unread)
        response = self.client.post(self.url, self.post_data)
        self.message4 = Message.objects.get(id=self.message4.id)
        self.message6 = Message.objects.get(id=self.message6.id)
        self.message8 = Message.objects.get(id=self.message8.id)
        self.assertFalse(self.message4.unread)
        self.assertFalse(self.message6.unread)
        self.assertFalse(self.message8.unread)

    def test_marks_all_messages_of_sender_as_viewed(self):
        self.assertTrue(Message.objects.filter(sender=self.sender2, recipient=self.user, unread=True).exists())
        self.assertTrue(Message.objects.filter(sender=self.sender3, recipient=self.user, unread=True).exists())
        self.assertTrue(Message.objects.filter(sender=self.sender4, recipient=self.user, unread=True).exists())
        response = self.client.post(self.url, self.post_data)
        self.assertFalse(Message.objects.filter(sender=self.sender2, recipient=self.user, unread=True).exists())
        self.assertFalse(Message.objects.filter(sender=self.sender3, recipient=self.user, unread=True).exists())
        self.assertFalse(Message.objects.filter(sender=self.sender4, recipient=self.user, unread=True).exists())

    def test_only_latest_3_user_messages_marked_as_viewed(self):
        self.assertTrue(Message.objects.filter(sender=self.sender1, recipient=self.user, unread=True).exists())
        self.assertTrue(Message.objects.filter(sender=self.sender2, recipient=self.user, unread=True).exists())
        self.assertTrue(Message.objects.filter(sender=self.sender3, recipient=self.user, unread=True).exists())
        self.assertTrue(Message.objects.filter(sender=self.sender4, recipient=self.user, unread=True).exists())
        response = self.client.post(self.url, self.post_data)
        self.assertTrue(Message.objects.filter(sender=self.sender1, recipient=self.user, unread=True).exists())
        self.assertFalse(Message.objects.filter(sender=self.sender2, recipient=self.user, unread=True).exists())
        self.assertFalse(Message.objects.filter(sender=self.sender3, recipient=self.user, unread=True).exists())
        self.assertFalse(Message.objects.filter(sender=self.sender4, recipient=self.user, unread=True).exists())

    def test_returns_403_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_returns_error_if_messages_ids_not_sent(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('message_sender_ids', response.data)
        self.assertIn('This field is required.', response.data['message_sender_ids'])


@pytest.mark.django_db
class TestMarkFriendRequestsViewed(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.user = CricketerFactory().user
        self.user2 = CricketerFactory().user
        self.user3 = CricketerFactory().user
        self.user4 = CricketerFactory().user
        self.friend_request1 = FriendRequestFactory(from_user=self.user2, to_user=self.user)
        self.friend_request2 = FriendRequestFactory(from_user=self.user3, to_user=self.user)
        self.friend_request3 = FriendRequestFactory(from_user=self.user4, to_user=self.user)

        self.post_data = {
            'friend_requests_viewed[]' : [self.friend_request1.id, self.friend_request2.id, self.friend_request3.id],
        }

        self.client.login(username=self.user.email, password=settings.TEST_USER_PASSWORD)
        self.url = reverse('mark_friend_requests_viewed')

    def test_returns_201_response_on_post(self):
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_marks_requests_as_viewed(self):
        self.assertFalse(self.friend_request1.viewed)
        self.assertFalse(self.friend_request2.viewed)
        self.assertFalse(self.friend_request3.viewed)
        response = self.client.post(self.url, self.post_data)
        self.friend_request1 = FriendRequest.objects.get(id=self.friend_request1.id)
        self.friend_request2 = FriendRequest.objects.get(id=self.friend_request2.id)
        self.friend_request3 = FriendRequest.objects.get(id=self.friend_request3.id)
        self.assertTrue(self.friend_request1.viewed)
        self.assertTrue(self.friend_request2.viewed)
        self.assertTrue(self.friend_request3.viewed)

    def test_returns_403_if_not_loggedin(self):
        self.client.session.flush()
        response = self.client.post(self.url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_returns_error_if_messages_ids_not_sent(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('friend_requests_viewed', response.data)
        self.assertIn('This field is required.', response.data['friend_requests_viewed'])

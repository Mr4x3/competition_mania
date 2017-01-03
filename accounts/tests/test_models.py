# inbuilt python imports
import unittest

# inbuilt django imports
from django.test import Client
from django.db.utils import IntegrityError
from django.template.defaultfilters import slugify
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

# third-party django imports
import pytest

# inter-app imports
from sportsvitae.shared.factories import UserFactory, MidoutUserFactory, CricketerFactory, ForeignUserFactory, FriendRequestFactory, MessageFactory, UserWallPostFactory, UserWallPostCommentFactory, CricketMatchStatFactory, CricketMatchBattingStatFactory, CricketMatchBowlingStatFactory, CricketTeamFactory, CricketMatchFactory, CricketTeamMemberFactory

# local imports
from ..models import User, FriendRequest, Message, UserWallPost, UserWallPostComment
from cricket.models import CricketMatchBattingStat, CricketMatchBowlingStat

@pytest.mark.django_db
class TestUser(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.cricketer = CricketerFactory(user__email='test@test.com')
        self.user = self.cricketer.user

    def test_instantiation(self):
        self.assertTrue(self.user)

    def test_object_created(self):
        self.assertTrue(User.objects.count())

    def test_correct_email(self):
        self.assertEqual(self.user.email, 'test@test.com')

    def test_cannot_violate_unique_email_constraint(self):
        self.assertRaises(IntegrityError, UserFactory, email='test@test.com')

    def test_password_stored_in_hashed_format(self):
        self.assertNotEqual(self.user.password, settings.TEST_USER_PASSWORD)
        self.assertTrue(self.user.check_password(settings.TEST_USER_PASSWORD))

    def test_correct_first_name(self):
        self.assertEqual(self.user.first_name, 'Jon')

    def test_correct_last_name(self):
        self.assertEqual(self.user.last_name, 'Snow')

    def test_correct_gender(self):
        self.assertEqual(self.user.gender, 'M')

    def test_correct_mobile(self):
        self.assertEqual(self.user.mobile, '9999999999')

    def test_correct_country(self):
        self.assertEqual(self.user.country, 'IN')

    def test_correct_state(self):
        self.assertEqual(self.user.state, 1013)

    def test_correct_state_text(self):
        self.assertEqual(self.user.state_text, '')

    def test_correct_city(self):
        self.assertEqual(self.user.city, 10178)

    def test_correct_city_text(self):
        self.assertEqual(self.user.city_text, '')

    def test_date_of_birth_none(self):
        self.assertIsNone(self.user.date_of_birth)

    def test_display_picture_none(self):
        self.assertIsNone(self.user.display_picture.name)
        with self.assertRaises(ValueError):
            self.user.display_picture.file

    def test_cover_picture_none(self):
        self.assertIsNone(self.user.cover_picture.name)
        with self.assertRaises(ValueError):
            self.user.display_picture.file

    def test_created_on_field_set(self):
        self.assertIsNotNone(self.user.created_on)

    def test_last_modified_set(self):
        self.assertIsNotNone(self.user.last_modified)

    def test_active_user(self):
        self.assertTrue(self.user.is_active)

    def test_not_staff_user(self):
        self.assertFalse(self.user.is_staff)

    def test_not_superuser(self):
        self.assertFalse(self.user.is_superuser)

    def test_registration_source_normal(self):
        self.assertEqual(self.user.registration_source, 1)

    def test_regisration_midout_set_to_false(self):
        self.assertFalse(self.user.registration_midout)

    def test_email_verified(self):
        self.assertTrue(self.user.is_email_verified)

    def test_slug_populated_automatically(self):
        self.assertTrue(self.user.slug)
        self.assertEqual(self.user.slug, slugify('Jon Snow 1'))

    def test_slug_updated_automatically_if_name_updated(self):
        self.assertEqual(self.user.slug, slugify('Jon Snow 1'))
        self.user.name = 'Tyrion Lannister'
        self.user.save()
        self.assertEqual(self.user.slug, slugify('Tyrion Lannister 1'))

    def test_slug_not_updated_if_updated_to_another_user_slug(self):
        old_slug = self.user.slug
        new_user = UserFactory(email='test2@test.com')
        self.user.slug = new_user.slug
        self.user.save()
        self.user = User.objects.get(email=self.user.email)
        self.assertNotEqual(self.user.slug, new_user.slug)
        self.assertEqual(self.user.slug, old_slug)

    def test_slug_not_updated_if_not_as_per_name_and_id(self):
        old_slug = self.user.slug
        new_slug = 'new-slug'
        self.user.slug = new_slug
        self.user.save()
        self.user = User.objects.get(email=self.user.email)
        self.assertNotEqual(self.user.slug, new_slug)
        self.assertEqual(self.user.slug, old_slug)

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), 'Jon Snow')

    def test_get_full_name_returns_capitalized_name(self):
        self.user.first_name = 'jon abc'
        self.user.last_name = 'night snow'
        self.user.save()
        self.assertEqual(self.user.get_full_name(), 'Jon Abc Night Snow')

    def test_get_short_name(self):
        self.assertEqual(self.user.get_short_name(), 'Jon')

    def test_is_registration_midout(self):
        self.assertEqual(self.user.is_registration_midout(), self.user.registration_midout)

    def test_has_sports_profile_method(self):
        self.user = UserFactory()
        self.assertFalse(self.user.has_sports_profile())

    def test_fullname_property(self):
        self.assertEqual(self.user.full_name, 'Jon Snow')

    def test_name_getter_property(self):
        self.assertEqual(self.user.name, 'Jon Snow')

    def test_name_setter_property(self):
        self.assertEqual(self.user.name, 'Jon Snow')
        self.user.name = 'Tyrion Lannister'
        self.user.save()
        self.user = User.objects.get(id=self.user.id)
        self.assertEqual(self.user.name, 'Tyrion Lannister')

    def test_country_code_property(self):
        self.assertEqual(self.user.country_code, '91')

    def test_user_from_india(self):
        self.assertTrue(self.user.from_india())
        self.assertFalse(self.user.is_foreigner())

    def test_get_state_display_value(self):
        self.assertEqual(self.user.get_state_display_value(), self.user.get_state_display())

    def test_get_state_text_display_value(self):
        self.user.state = None
        self.user.state_text = 'Ohio'
        self.user.save()
        self.assertEqual(self.user.get_state_display_value(), self.user.state_text)

    def test_user_foreigner_if_non_indian_country(self):
        foreigner = ForeignUserFactory()
        self.assertTrue(foreigner.is_foreigner())
        self.assertFalse(foreigner.from_india())

    def test_get_city_display_value(self):
        self.assertEqual(self.user.get_city_display_value(), self.user.get_city_display())

    def test_get_city_text_display_value(self):
        self.user.city = None
        self.user.city_text = '21 Baker Street'
        self.user.save()
        self.assertEqual(self.user.get_city_display_value(), self.user.city_text)

    def test_initially_has_no_friends(self):
        self.assertFalse(self.user.friends.all())

    def test_user_can_add_a_friend(self):
        self.assertEqual(self.user.friends.all().count(), 0)
        cricketer2 = CricketerFactory()
        user2 = cricketer2.user
        self.user.add_friend(user2)
        self.assertTrue(self.user.friends.filter(id=user2.id).exists())
        self.assertEqual(self.user.friends.all().count(), 1)

    def test_other_user_also_has_a_friend(self):
        cricketer2 = CricketerFactory()
        user2 = cricketer2.user
        self.assertEqual(user2.friends.all().count(), 0)
        user2.add_friend(self.user)
        self.assertTrue(user2.friends.filter(id=self.user.id).exists())
        self.assertEqual(user2.friends.all().count(), 1)

    def test_cannot_add_same_friend_twice(self):
        self.assertEqual(self.user.friends.all().count(), 0)
        cricketer2 = CricketerFactory()
        user2 = cricketer2.user
        self.user.add_friend(user2)
        self.assertEqual(self.user.friends.all().count(), 1)
        self.user.add_friend(user2)
        self.assertEqual(self.user.friends.all().count(), 1)

    def test_user_cannot_add_self_as_friend(self):
        self.assertRaises(ValidationError, self.user.add_friend, self.user)

    def test_remove_friend(self):
        cricketer2 = CricketerFactory()
        user2 = cricketer2.user
        self.user.add_friend(user2)
        self.assertEqual(self.user.friends.all().count(), 1)
        self.user.remove_friend(user2)
        self.assertEqual(self.user.friends.all().count(), 0)

    def test_cannot_remove_self_as_friend(self):
        self.assertRaises(ValidationError, self.user.remove_friend, self.user)

    def test_remove_friend_from_other_side_also(self):
        cricketer2 = CricketerFactory()
        user2 = cricketer2.user
        self.user.add_friend(user2)
        self.assertEqual(user2.friends.all().count(), 1)
        user2.remove_friend(self.user)
        self.assertEqual(user2.friends.all().count(), 0)

    def test_no_error_on_remove_non_friend_user(self):
        user2 = UserFactory()
        try:
            self.user.remove_friend(user2)
        except:
            self.fail("Cannot remove a non-friend user.")

    def test_returns_incomplete_user_for_no_sports_profile(self):
        user = UserFactory()
        self.assertFalse(user.is_registration_midout())
        self.assertFalse(user.has_sports_profile())
        self.assertFalse(user.is_complete_user())

    def test_returns_incomplete_user_for_midout(self):
        user = MidoutUserFactory()
        self.assertTrue(user.is_registration_midout())
        self.assertFalse(user.is_complete_user())

    def test_returns_complete_user_for_cricketer(self):
        cricketer = CricketerFactory()
        user = cricketer.user
        self.assertFalse(self.user.is_registration_midout())
        self.assertTrue(self.user.has_sports_profile())
        self.assertTrue(self.user.is_complete_user())

    def test_returns_no_friend_suggestions(self):
        self.assertFalse(self.user.get_friend_suggestions())

    def test_returns_friend_suggestion_for_another_user_with_same_city(self):
        user2 = UserFactory()
        user3 = UserFactory()
        friend_suggestions = self.user.get_friend_suggestions()
        self.assertEqual(friend_suggestions.count(), 2)
        self.assertTrue(friend_suggestions.filter(id=user2.id).exists())
        self.assertTrue(friend_suggestions.filter(id=user3.id).exists())

    def test_does_not_return_friend_suggestion_if_friend_request_already_sent(self):
        User.objects.all().delete()
        cricketer1 = CricketerFactory()
        user1 = cricketer1.user
        cricketer2 = CricketerFactory()
        user2 = cricketer2.user
        cricketer3 = CricketerFactory()
        user3 = cricketer3.user
        FriendRequestFactory(cricketer1=cricketer1, cricketer2=cricketer2)
        friend_suggestions = user1.get_friend_suggestions()
        self.assertNotEqual(friend_suggestions.count(), 2)
        self.assertEqual(friend_suggestions.count(), 1)
        self.assertFalse(friend_suggestions.filter(id=user2.id).exists())
        self.assertTrue(friend_suggestions.filter(id=user3.id).exists())

    def test_does_not_return_self_as_friend_suggestion(self):
        user2 = UserFactory()
        user3 = UserFactory()
        friend_suggestions = self.user.get_friend_suggestions()
        self.assertTrue(friend_suggestions)
        self.assertFalse(friend_suggestions.filter(id=self.user.id).exists())

    def test_does_not_return_existing_friend_as_suggestion(self):
        User.objects.all().delete()
        cricketer1 = CricketerFactory()
        user1 = cricketer1.user
        cricketer2 = CricketerFactory()
        user2 = cricketer2.user
        cricketer3 = CricketerFactory()
        user3 = cricketer3.user
        user1.add_friend(user2)
        friend_suggestions = user1.get_friend_suggestions()
        self.assertEqual(friend_suggestions.count(), 1)
        self.assertFalse(friend_suggestions.filter(id=user2.id).exists())

    def test_returns_friend_suggestion_for_international_user_with_same_city(self):
        User.objects.all().delete()
        user1 = ForeignUserFactory()
        user2 = ForeignUserFactory()
        user3 = ForeignUserFactory()
        cricketer1 = CricketerFactory(user=user1)
        cricketer2 = CricketerFactory(user=user2)
        cricketer3 = CricketerFactory(user=user3)
        friend_suggestions = user1.get_friend_suggestions()
        self.assertEqual(friend_suggestions.count(), 2)
        self.assertTrue(friend_suggestions.filter(id=user2.id).exists())
        self.assertTrue(friend_suggestions.filter(id=user3.id).exists())

    def test_does_not_return_self_as_friend_suggestion(self):
        User.objects.all().delete()
        user1 = ForeignUserFactory()
        user2 = ForeignUserFactory()
        user3 = ForeignUserFactory()
        cricketer1 = CricketerFactory(user=user1)
        cricketer2 = CricketerFactory(user=user2)
        cricketer3 = CricketerFactory(user=user3)
        friend_suggestions = user1.get_friend_suggestions()
        self.assertTrue(friend_suggestions)
        self.assertFalse(friend_suggestions.filter(id=user1.id).exists())

    def test_does_not_return_existing_friend_as_suggestion(self):
        User.objects.all().delete()
        user1 = ForeignUserFactory()
        user2 = ForeignUserFactory()
        user3 = ForeignUserFactory()
        cricketer1 = CricketerFactory(user=user1)
        cricketer2 = CricketerFactory(user=user2)
        cricketer3 = CricketerFactory(user=user3)
        user1.add_friend(user2)
        friend_suggestions = user1.get_friend_suggestions()
        self.assertEqual(friend_suggestions.count(), 1)
        self.assertFalse(friend_suggestions.filter(id=user2.id).exists())

    def test_returns_no_team_follow_suggestions_for_midout_user(self):
        user = MidoutUserFactory()
        team_follow_suggestions = user.get_team_follow_suggestions()
        self.assertFalse(team_follow_suggestions)

    def test_returns_no_team_follow_suggestions_for_no_sports_profile_user(self):
        user = UserFactory()
        team_follow_suggestions = user.get_team_follow_suggestions()
        self.assertFalse(team_follow_suggestions)

    def test_does_not_return_team_follow_suggestion_for_ex_team(self):
        friend1 = CricketerFactory().user
        self.user.friends.add(friend1)
        team_member = CricketTeamMemberFactory(cricketer=friend1.cricketer, is_active=False)
        team_follow_suggestions = self.user.get_team_follow_suggestions()
        self.assertFalse(team_follow_suggestions)

    def test_returns_team_follow_suggestions_for_team(self):
        friend1 = CricketerFactory().user
        self.user.friends.add(friend1)
        team_member = CricketTeamMemberFactory(cricketer=friend1.cricketer)
        team_follow_suggestions = self.user.get_team_follow_suggestions()
        self.assertTrue(team_follow_suggestions)
        self.assertIn(team_member.team, team_follow_suggestions)

    def test_does_not_return_team_follow_suggestions_for_deleted_team(self):
        team2 = CricketTeamFactory(is_deleted=True)
        friend1 = CricketerFactory().user
        self.user.friends.add(friend1)
        team_member = CricketTeamMemberFactory(team=team2, cricketer=friend1.cricketer)
        team_follow_suggestions = self.user.get_team_follow_suggestions()
        self.assertFalse(team_follow_suggestions)

    def test_returns_all_friend_requests(self):
        FriendRequest.objects.all().delete()
        user2 = CricketerFactory().user
        user3 = CricketerFactory().user
        user4 = CricketerFactory().user
        user5 = CricketerFactory().user
        friend_request1 = FriendRequestFactory(from_user=user2, to_user=self.user)
        friend_request2 = FriendRequestFactory(from_user=user3, to_user=self.user)
        friend_request3 = FriendRequestFactory(from_user=user4, to_user=self.user)
        friend_request4 = FriendRequestFactory(from_user=user5, to_user=self.user)
        friend_requests = self.user.get_all_friend_requests()
        self.assertEqual(len(friend_requests), 4)
        self.assertIn(friend_request1, friend_requests)
        self.assertIn(friend_request2, friend_requests)
        self.assertIn(friend_request3, friend_requests)
        self.assertIn(friend_request4, friend_requests)

    def test_returns_only_non_accepted_friend_requests(self):
        FriendRequest.objects.all().delete()
        user2 = CricketerFactory().user
        user3 = CricketerFactory().user
        friend_request1 = FriendRequestFactory(from_user=user2, to_user=self.user)
        friend_request2 = FriendRequestFactory(from_user=user3, to_user=self.user, accepted=True)
        friend_requests = self.user.get_all_friend_requests()
        self.assertEqual(len(friend_requests), 1)
        self.assertIn(friend_request1, friend_requests)
        self.assertNotIn(friend_request2, friend_requests)

    def test_returns_all_friend_requests_in_sorted_order(self):
        FriendRequest.objects.all().delete()
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        friend_request1 = FriendRequestFactory(from_user=friend1, to_user=self.user)
        friend_request2 = FriendRequestFactory(from_user=friend2, to_user=self.user)
        friend_requests = self.user.get_all_friend_requests()
        self.assertEqual(len(friend_requests), 2)
        self.assertEqual(friend_requests, [friend_request2, friend_request1])

    def test_returns_friend_requests_sorted_by_those_not_viewed_first(self):
        FriendRequest.objects.all().delete()
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        friend3 = CricketerFactory().user
        friend4 = CricketerFactory().user
        friend_request1 = FriendRequestFactory(from_user=friend1, to_user=self.user, viewed=True)
        friend_request2 = FriendRequestFactory(from_user=friend2, to_user=self.user, viewed=False)
        friend_request3 = FriendRequestFactory(from_user=friend3, to_user=self.user, viewed=True)
        friend_request4 = FriendRequestFactory(from_user=friend4, to_user=self.user, viewed=False)
        friend_requests = self.user.get_all_friend_requests()
        self.assertEqual(len(friend_requests), 4)
        self.assertEqual(friend_requests, [friend_request4, friend_request2, friend_request3, friend_request1])

    def test_returns_friend_requests_sorted_by_those_not_viewed_first_and_then_by_latest_created(self):
        FriendRequest.objects.all().delete()
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        friend3 = CricketerFactory().user
        friend4 = CricketerFactory().user
        friend_request1 = FriendRequestFactory(from_user=friend1, to_user=self.user, viewed=True)
        friend_request2 = FriendRequestFactory(from_user=friend2, to_user=self.user, viewed=False)
        friend_request3 = FriendRequestFactory(from_user=friend3, to_user=self.user, viewed=True)
        friend_request4 = FriendRequestFactory(from_user=friend4, to_user=self.user, viewed=False)
        friend_requests = self.user.get_all_friend_requests()
        self.assertEqual(len(friend_requests), 4)
        self.assertEqual(friend_requests, [friend_request4, friend_request2, friend_request3, friend_request1])

    def test_latest_friend_requests_returns_3_friend_requests(self):
        FriendRequest.objects.all().delete()
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        friend3 = CricketerFactory().user
        friend4 = CricketerFactory().user
        friend_request1 = FriendRequestFactory(from_user=friend1, to_user=self.user, viewed=True)
        friend_request2 = FriendRequestFactory(from_user=friend2, to_user=self.user, viewed=False)
        friend_request3 = FriendRequestFactory(from_user=friend3, to_user=self.user, viewed=True)
        friend_request4 = FriendRequestFactory(from_user=friend4, to_user=self.user, viewed=False)
        latest_friend_requests = self.user.get_latest_friend_requests()
        self.assertEqual(len(latest_friend_requests), 3)
        self.assertEqual(latest_friend_requests, [friend_request4, friend_request2, friend_request3])

    def test_get_latest_messages_returns_latest_message_of_last_3_messaged_friends(self):
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        friend3 = CricketerFactory().user
        friend4 = CricketerFactory().user
        message1 = MessageFactory(sender=friend1, recipient=self.user)
        message2 = MessageFactory(sender=friend1, recipient=self.user)
        message3 = MessageFactory(sender=friend2, recipient=self.user)
        message4 = MessageFactory(sender=friend2, recipient=self.user)
        message5 = MessageFactory(sender=friend3, recipient=self.user)
        message6 = MessageFactory(sender=friend3, recipient=self.user)
        message7 = MessageFactory(sender=friend4, recipient=self.user)
        message8 = MessageFactory(sender=friend4, recipient=self.user)
        latest_messages = list(self.user.get_latest_received_messages())
        self.assertEqual(len(latest_messages), 3)
        self.assertEqual(latest_messages, [message8, message6, message4])

    def test_get_latest_messages_does_not_return_sent_message(self):
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        friend3 = CricketerFactory().user
        friend4 = CricketerFactory().user
        message1 = MessageFactory(sender=friend1, recipient=self.user)
        message2 = MessageFactory(sender=friend1, recipient=self.user)
        message3 = MessageFactory(sender=friend2, recipient=self.user)
        message4 = MessageFactory(sender=friend2, recipient=self.user)
        message5 = MessageFactory(sender=friend3, recipient=self.user)
        message6 = MessageFactory(sender=friend3, recipient=self.user)
        message7 = MessageFactory(sender=friend4, recipient=self.user)
        message8 = MessageFactory(sender=friend4, recipient=self.user)
        message9 = MessageFactory(sender=self.user, recipient=friend4)
        latest_messages = list(self.user.get_latest_received_messages())
        self.assertEqual(len(latest_messages), 3)
        self.assertNotIn(message9, latest_messages)

    def test_returns_no_messages_if_no_messages(self):
        Message.objects.all().delete()
        latest_messages = list(self.user.get_latest_received_messages())
        self.assertEqual(latest_messages, [])

    def test_get_latest_messages_returns_latest_message_in_unread_order(self):
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        friend3 = CricketerFactory().user
        friend4 = CricketerFactory().user
        message1 = MessageFactory(sender=friend1, recipient=self.user)
        message2 = MessageFactory(sender=friend1, recipient=self.user)
        message3 = MessageFactory(sender=friend2, recipient=self.user, unread=False)
        message4 = MessageFactory(sender=friend2, recipient=self.user)
        message5 = MessageFactory(sender=friend3, recipient=self.user)
        message6 = MessageFactory(sender=friend3, recipient=self.user, unread=False)
        message7 = MessageFactory(sender=friend4, recipient=self.user)
        message8 = MessageFactory(sender=friend4, recipient=self.user)
        latest_messages = list(self.user.get_latest_received_messages())
        self.assertEqual(len(latest_messages), 3)
        self.assertEqual(latest_messages, [message8, message5, message4])

    def test_get_latest_messages_returns_latest_message_only_for_each_user(self):
        friend1 = CricketerFactory().user
        message1 = MessageFactory(sender=friend1, recipient=self.user)
        message2 = MessageFactory(sender=friend1, recipient=self.user)
        message3 = MessageFactory(sender=friend1, recipient=self.user, unread=False)
        latest_messages = list(self.user.get_latest_received_messages())
        self.assertEqual(len(latest_messages), 1)
        self.assertEqual(latest_messages, [message2])

    def test_get_chat_between_friend_returns_all_messages_between_that_friend(self):
        friend1 = CricketerFactory().user
        message1 = MessageFactory(sender=friend1, recipient=self.user)
        message2 = MessageFactory(sender=self.user, recipient=friend1)
        message3 = MessageFactory(sender=friend1, recipient=self.user)
        message4 = MessageFactory(sender=friend1, recipient=self.user)
        chat_history = list(self.user.get_chat_between_friend(friend1))
        self.assertEqual(len(chat_history), 4)
        self.assertEqual(chat_history, [message1, message2, message3, message4])

    def test_get_chat_between_friend_returns_no_messages_if_no_messages(self):
        friend1 = CricketerFactory().user
        chat_history = list(self.user.get_chat_between_friend(friend1))
        self.assertEqual(len(chat_history), 0)

    def test_get_get_all_friends_messaged_returns_all_friends_with_mutual_chat_history(self):
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        friend3 = CricketerFactory().user
        friend4 = CricketerFactory().user
        self.user.add_friend(friend1)
        self.user.add_friend(friend2)
        self.user.add_friend(friend3)
        self.user.add_friend(friend4)
        message1 = MessageFactory(sender=friend1, recipient=self.user)
        message2 = MessageFactory(sender=self.user, recipient=friend1)
        message3 = MessageFactory(sender=friend2, recipient=self.user)
        message4 = MessageFactory(sender=self.user, recipient=friend2)
        message5 = MessageFactory(sender=friend3, recipient=self.user)
        message6 = MessageFactory(sender=self.user, recipient=friend3)
        message7 = MessageFactory(sender=friend4, recipient=self.user)
        message8 = MessageFactory(sender=self.user, recipient=friend4)
        all_friends_messaged = self.user.get_all_friends_messaged()
        self.assertEqual(len(all_friends_messaged), 4)

    def test_get_get_all_friends_messaged_returns_all_friends_sorted_by_latest_chat_first(self):
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        friend3 = CricketerFactory().user
        friend4 = CricketerFactory().user
        self.user.add_friend(friend1)
        self.user.add_friend(friend2)
        self.user.add_friend(friend3)
        self.user.add_friend(friend4)
        message1 = MessageFactory(sender=friend1, recipient=self.user)
        message2 = MessageFactory(sender=self.user, recipient=friend1)
        message3 = MessageFactory(sender=friend2, recipient=self.user)
        message4 = MessageFactory(sender=self.user, recipient=friend2)
        message5 = MessageFactory(sender=friend3, recipient=self.user)
        message6 = MessageFactory(sender=self.user, recipient=friend3)
        message7 = MessageFactory(sender=friend4, recipient=self.user)
        message8 = MessageFactory(sender=self.user, recipient=friend4)
        all_friends_messaged = self.user.get_all_friends_messaged()
        self.assertEqual(all_friends_messaged, [friend4, friend3, friend2, friend1])

    def test_not_return_other_user_if_not_friend_in_get_all_friends_messaged(self):
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        friend3 = CricketerFactory().user
        friend4 = CricketerFactory().user
        self.user.add_friend(friend1)
        self.user.add_friend(friend2)
        friend3.add_friend(friend4)
        message1 = MessageFactory(sender=friend1, recipient=self.user)
        message2 = MessageFactory(sender=self.user, recipient=friend1)
        message3 = MessageFactory(sender=friend2, recipient=self.user)
        message4 = MessageFactory(sender=self.user, recipient=friend2)
        message5 = MessageFactory(sender=friend3, recipient=friend4)
        all_friends_messaged = self.user.get_all_friends_messaged()
        self.assertEqual(len(all_friends_messaged), 2)
        self.assertNotIn(friend3, all_friends_messaged)
        self.assertNotIn(friend4, all_friends_messaged)

    def test_returns_best_batting_performance(self):
        cricketer = CricketerFactory()
        user = cricketer.user
        batting_stat1 = CricketMatchBattingStatFactory(batsman=cricketer, runs=100, balls_played=30, sixes=10)
        batting_stat2 = CricketMatchBattingStatFactory(batsman=cricketer, runs=40, balls_played=30)
        batting_stat3 = CricketMatchBattingStatFactory(batsman=cricketer, runs=100, balls_played=20, fours=6)
        batting_stat4 = CricketMatchBattingStatFactory(batsman=cricketer, runs=60, balls_played=30)
        batting_stat5 = CricketMatchBattingStatFactory(batsman=cricketer, runs=20)
        best_batting_performance = user.get_best_batting_performance()
        self.assertEqual(best_batting_performance['highest_score_runs'], 100)
        self.assertEqual(best_batting_performance['highest_score_balls_played'], 20)
        self.assertEqual(best_batting_performance['max_fours'], 6)
        self.assertEqual(best_batting_performance['max_sixes'], 10)
        self.assertEqual(best_batting_performance['fifties'], 1)
        self.assertEqual(best_batting_performance['hundreds'], 2)

    def test_returns_best_bowling_performance(self):
        cricketer = CricketerFactory()
        user = cricketer.user
        bowling_stat1 = CricketMatchBowlingStatFactory(bowler=cricketer, runs=100, wickets=5)
        bowling_stat2 = CricketMatchBowlingStatFactory(bowler=cricketer, runs=40, wickets=5)
        bowling_stat3 = CricketMatchBowlingStatFactory(bowler=cricketer, runs=100, wickets=3)
        bowling_stat4 = CricketMatchBowlingStatFactory(bowler=cricketer, runs=60, wickets=2)
        bowling_stat5 = CricketMatchBowlingStatFactory(bowler=cricketer, runs=20)
        best_bowling_performance = user.get_best_bowling_performance()
        self.assertEqual(best_bowling_performance['best_bowling_wickets'], 5)
        self.assertEqual(best_bowling_performance['best_bowling_runs'], 40)
        self.assertEqual(best_bowling_performance['three_wicket_hauls'], 3)
        self.assertEqual(best_bowling_performance['five_wicket_hauls'], 2)

    def test_returns_no_best_batting_performance_if_no_batting_stats(self):
        cricketer = CricketerFactory()
        user = cricketer.user
        CricketMatchBattingStat.objects.all().delete()
        self.assertEqual(user.get_best_batting_performance(), {})

    def test_returns_no_best_bowling_performance_if_no_bowling_stats(self):
        cricketer = CricketerFactory()
        user = cricketer.user
        CricketMatchBowlingStat.objects.all().delete()
        self.assertEqual(user.get_best_bowling_performance(), {})

    def test_returns_no_best_performance_if_no_performance(self):
        cricketer = CricketerFactory()
        user = cricketer.user
        CricketMatchBattingStat.objects.all().delete()
        CricketMatchBowlingStat.objects.all().delete()
        self.assertEqual(user.get_best_performance_stats(), {})

    def test_returns_best_performance_stats(self):
        cricketer = CricketerFactory()
        user = cricketer.user

        batting_stat1 = CricketMatchBattingStatFactory(batsman=cricketer, runs=100, balls_played=30, sixes=10)
        batting_stat2 = CricketMatchBattingStatFactory(batsman=cricketer, runs=40, balls_played=30)
        batting_stat3 = CricketMatchBattingStatFactory(batsman=cricketer, runs=100, balls_played=20, fours=6)
        batting_stat4 = CricketMatchBattingStatFactory(batsman=cricketer, runs=60, balls_played=30)
        batting_stat5 = CricketMatchBattingStatFactory(batsman=cricketer, runs=20)
        bowling_stat1 = CricketMatchBowlingStatFactory(bowler=cricketer, runs=100, wickets=5)
        bowling_stat2 = CricketMatchBowlingStatFactory(bowler=cricketer, runs=40, wickets=5)
        bowling_stat3 = CricketMatchBowlingStatFactory(bowler=cricketer, runs=100, wickets=3)
        bowling_stat4 = CricketMatchBowlingStatFactory(bowler=cricketer, runs=60, wickets=2)
        bowling_stat5 = CricketMatchBowlingStatFactory(bowler=cricketer, runs=20)

        best_performance_stats = user.get_best_performance_stats()

        self.assertEqual(best_performance_stats['highest_score_runs'], 100)
        self.assertEqual(best_performance_stats['highest_score_balls_played'], 20)
        self.assertEqual(best_performance_stats['max_fours'], 6)
        self.assertEqual(best_performance_stats['max_sixes'], 10)
        self.assertEqual(best_performance_stats['fifties'], 1)
        self.assertEqual(best_performance_stats['hundreds'], 2)
        self.assertEqual(best_performance_stats['best_bowling_wickets'], 5)
        self.assertEqual(best_performance_stats['best_bowling_runs'], 40)
        self.assertEqual(best_performance_stats['three_wicket_hauls'], 3)
        self.assertEqual(best_performance_stats['five_wicket_hauls'], 2)

    def test_get_overall_batting_career_stats_returns_no_stats_if_empty(self):
        cricketer = CricketerFactory()
        user = cricketer.user
        CricketMatchBattingStat.objects.all().delete()
        self.assertEqual(user.get_overall_batting_career_stats(), {})

    def test_get_overall_bowling_career_stats_returns_no_stats_if_empty(self):
        cricketer = CricketerFactory()
        user = cricketer.user
        CricketMatchBowlingStat.objects.all().delete()
        self.assertEqual(user.get_overall_bowling_career_stats(), {})

    def test_get_overall_batting_career_stats_returns_total_matches_with_batting_stat_empty(self):
        cricketer = CricketerFactory()
        user = cricketer.user
        team = CricketTeamFactory()

        member1 = CricketTeamMemberFactory(team=team, cricketer=cricketer, is_super_admin=True)
        member2 = CricketTeamMemberFactory(team=team)
        member3 = CricketTeamMemberFactory(team=team)
        member4 = CricketTeamMemberFactory(team=team)
        member5 = CricketTeamMemberFactory(team=team)
        member6 = CricketTeamMemberFactory(team=team)
        member7 = CricketTeamMemberFactory(team=team)
        member8 = CricketTeamMemberFactory(team=team)
        member9 = CricketTeamMemberFactory(team=team)
        member10 = CricketTeamMemberFactory(team=team)
        member11 = CricketTeamMemberFactory(team=team)

        playing_eleven = [member1, member2, member3, member4, member5, member6, member7, member8, member9, member10, member11]

        match1 = CricketMatchFactory(team=team, playing_eleven=playing_eleven)
        match_stat1 = CricketMatchStatFactory(match=match1)
        match_stat2 = CricketMatchStatFactory(match=None) # user stat

        bowling_stat1 = CricketMatchBowlingStatFactory(match_stat=match_stat2, bowler=cricketer, runs=100, wickets=5, overs=2)

        overall_batting_career_stats = user.get_overall_batting_career_stats()

        self.assertEqual(overall_batting_career_stats['total_matches'], 2)

    def test_get_overall_batting_career_stats_returns_career_batting_stats(self):
        cricketer = CricketerFactory()
        user = cricketer.user
        team = CricketTeamFactory()

        member1 = CricketTeamMemberFactory(team=team, cricketer=cricketer, is_super_admin=True)
        member2 = CricketTeamMemberFactory(team=team)
        member3 = CricketTeamMemberFactory(team=team)
        member4 = CricketTeamMemberFactory(team=team)
        member5 = CricketTeamMemberFactory(team=team)
        member6 = CricketTeamMemberFactory(team=team)
        member7 = CricketTeamMemberFactory(team=team)
        member8 = CricketTeamMemberFactory(team=team)
        member9 = CricketTeamMemberFactory(team=team)
        member10 = CricketTeamMemberFactory(team=team)
        member11 = CricketTeamMemberFactory(team=team)

        playing_eleven = [member1, member2, member3, member4, member5, member6, member7, member8, member9, member10, member11]

        match1 = CricketMatchFactory(team=team, playing_eleven=playing_eleven)
        match_stat1 = CricketMatchStatFactory(match=match1)

        batting_stat1 = CricketMatchBattingStatFactory(batsman=cricketer, runs=100, balls_played=30, fours=4, sixes=10)
        batting_stat2 = CricketMatchBattingStatFactory(batsman=cricketer, runs=40, balls_played=30, fours=2, sixes=2)
        batting_stat3 = CricketMatchBattingStatFactory(batsman=cricketer, runs=100, balls_played=20, fours=2, sixes=2)
        batting_stat4 = CricketMatchBattingStatFactory(batsman=cricketer, runs=60, balls_played=30, dismissal_method='RH', fours=2, sixes=2)
        batting_stat5 = CricketMatchBattingStatFactory(batsman=cricketer, runs=20, balls_played=30, dismissal_method='NO', fours=2, sixes=2)
        batting_stat6 = CricketMatchBattingStatFactory(batsman=cricketer, runs=20, balls_played=30, fours=2, sixes=2)
        batting_stat7 = CricketMatchBattingStatFactory(runs=20, balls_played=30, dismissal_method='NO', fours=2, sixes=2)

        overall_batting_career_stats = user.get_overall_batting_career_stats()

        self.assertEqual(overall_batting_career_stats['total_matches'], 7)
        self.assertEqual(overall_batting_career_stats['total_batting_innings'], 6)
        self.assertEqual(overall_batting_career_stats['not_out_innings_count'], 2)
        self.assertEqual(overall_batting_career_stats['total_runs'], 340)
        self.assertEqual(overall_batting_career_stats['total_balls_played'], 170)
        self.assertEqual(overall_batting_career_stats['fours'], 14)
        self.assertEqual(overall_batting_career_stats['sixes'], 20)
        self.assertEqual(overall_batting_career_stats['batting_average'], 85)
        self.assertEqual(overall_batting_career_stats['batting_strike_rate'], 200)
        self.assertEqual(overall_batting_career_stats['fifties'], 1)
        self.assertEqual(overall_batting_career_stats['hundreds'], 2)
        self.assertEqual(overall_batting_career_stats['highest_score'], 100)

    def test_get_overall_bowling_career_stats_returns_career_bowling_stats(self):
        cricketer = CricketerFactory()
        user = cricketer.user
        team = CricketTeamFactory()

        member1 = CricketTeamMemberFactory(team=team, cricketer=cricketer, is_super_admin=True)
        member2 = CricketTeamMemberFactory(team=team)
        member3 = CricketTeamMemberFactory(team=team)
        member4 = CricketTeamMemberFactory(team=team)
        member5 = CricketTeamMemberFactory(team=team)
        member6 = CricketTeamMemberFactory(team=team)
        member7 = CricketTeamMemberFactory(team=team)
        member8 = CricketTeamMemberFactory(team=team)
        member9 = CricketTeamMemberFactory(team=team)
        member10 = CricketTeamMemberFactory(team=team)
        member11 = CricketTeamMemberFactory(team=team)

        playing_eleven = [member1, member2, member3, member4, member5, member6, member7, member8, member9, member10, member11]

        match1 = CricketMatchFactory(team=team, playing_eleven=playing_eleven)
        match_stat1 = CricketMatchStatFactory(match=match1)

        bowling_stat1 = CricketMatchBowlingStatFactory(bowler=cricketer, runs=100, wickets=5, overs=2)
        bowling_stat2 = CricketMatchBowlingStatFactory(bowler=cricketer, runs=40, wickets=5, overs=2.4)
        bowling_stat3 = CricketMatchBowlingStatFactory(bowler=cricketer, runs=80, wickets=3, overs=2.0)
        bowling_stat4 = CricketMatchBowlingStatFactory(bowler=cricketer, runs=60, wickets=2, overs=1.0)
        bowling_stat5 = CricketMatchBowlingStatFactory(bowler=cricketer, runs=20, wickets=5, overs=2.2)

        overall_bowling_career_stats = user.get_overall_bowling_career_stats()

        self.assertEqual(overall_bowling_career_stats['total_matches'], 6)
        self.assertEqual(overall_bowling_career_stats['total_balls_bowled'], 60)
        self.assertEqual(overall_bowling_career_stats['total_runs_conceded'], 300)
        self.assertEqual(overall_bowling_career_stats['total_wickets'], 20)
        self.assertEqual(overall_bowling_career_stats['economy'], 30)
        self.assertEqual(overall_bowling_career_stats['bowling_average'], 15)
        self.assertEqual(overall_bowling_career_stats['best_bowling_wickets'], 5)
        self.assertEqual(overall_bowling_career_stats['best_bowling_runs'], 20)

    def test_get_overall_bowling_career_stats_returns_empty_keys_if_no_bowling_stats_but_matches_played(self):
        cricketer = CricketerFactory()
        user = cricketer.user
        team = CricketTeamFactory()

        member1 = CricketTeamMemberFactory(team=team, cricketer=cricketer, is_super_admin=True)
        member2 = CricketTeamMemberFactory(team=team)
        member3 = CricketTeamMemberFactory(team=team)
        member4 = CricketTeamMemberFactory(team=team)
        member5 = CricketTeamMemberFactory(team=team)
        member6 = CricketTeamMemberFactory(team=team)
        member7 = CricketTeamMemberFactory(team=team)
        member8 = CricketTeamMemberFactory(team=team)
        member9 = CricketTeamMemberFactory(team=team)
        member10 = CricketTeamMemberFactory(team=team)
        member11 = CricketTeamMemberFactory(team=team)

        playing_eleven = [member1, member2, member3, member4, member5, member6, member7, member8, member9, member10, member11]

        match1 = CricketMatchFactory(team=team, playing_eleven=playing_eleven)
        match_stat1 = CricketMatchStatFactory(match=match1)

        overall_bowling_career_stats = user.get_overall_bowling_career_stats()

        self.assertEqual(overall_bowling_career_stats['total_matches'], 1)
        self.assertEqual(overall_bowling_career_stats['total_balls_bowled'], 0)
        self.assertEqual(overall_bowling_career_stats['total_runs_conceded'], 0)
        self.assertEqual(overall_bowling_career_stats['total_wickets'], 0)
        self.assertEqual(overall_bowling_career_stats['economy'], 0)
        self.assertEqual(overall_bowling_career_stats['bowling_average'], 0)
        self.assertEqual(overall_bowling_career_stats['best_bowling_wickets'], 0)
        self.assertEqual(overall_bowling_career_stats['best_bowling_runs'], 0)

    def test_get_overall_batting_career_stats_returns_empty_keys_if_no_batting_stats_but_matches_played(self):
        cricketer = CricketerFactory()
        user = cricketer.user
        team = CricketTeamFactory()

        member1 = CricketTeamMemberFactory(team=team, cricketer=cricketer, is_super_admin=True)
        member2 = CricketTeamMemberFactory(team=team)
        member3 = CricketTeamMemberFactory(team=team)
        member4 = CricketTeamMemberFactory(team=team)
        member5 = CricketTeamMemberFactory(team=team)
        member6 = CricketTeamMemberFactory(team=team)
        member7 = CricketTeamMemberFactory(team=team)
        member8 = CricketTeamMemberFactory(team=team)
        member9 = CricketTeamMemberFactory(team=team)
        member10 = CricketTeamMemberFactory(team=team)
        member11 = CricketTeamMemberFactory(team=team)

        playing_eleven = [member1, member2, member3, member4, member5, member6, member7, member8, member9, member10, member11]

        match1 = CricketMatchFactory(team=team, playing_eleven=playing_eleven)
        match_stat1 = CricketMatchStatFactory(match=match1)

        overall_batting_career_stats = user.get_overall_batting_career_stats()

        self.assertEqual(overall_batting_career_stats['total_matches'], 1)
        self.assertEqual(overall_batting_career_stats['total_batting_innings'], 0)
        self.assertEqual(overall_batting_career_stats['not_out_innings_count'], 0)
        self.assertEqual(overall_batting_career_stats['total_runs'], 0)
        self.assertEqual(overall_batting_career_stats['total_balls_played'], 0)
        self.assertEqual(overall_batting_career_stats['fours'], 0)
        self.assertEqual(overall_batting_career_stats['sixes'], 0)
        self.assertEqual(overall_batting_career_stats['batting_average'], 0)
        self.assertEqual(overall_batting_career_stats['batting_strike_rate'], 0)
        self.assertEqual(overall_batting_career_stats['fifties'], 0)
        self.assertEqual(overall_batting_career_stats['hundreds'], 0)
        self.assertEqual(overall_batting_career_stats['highest_score'], 0)

    def test_get_overall_batting_career_stats_returns_career_batting_stats_in_teams(self):
        cricketer = CricketerFactory()
        user = cricketer.user
        team = CricketTeamFactory()

        member1 = CricketTeamMemberFactory(team=team, cricketer=cricketer, is_super_admin=True)
        member2 = CricketTeamMemberFactory(team=team)
        member3 = CricketTeamMemberFactory(team=team)
        member4 = CricketTeamMemberFactory(team=team)
        member5 = CricketTeamMemberFactory(team=team)
        member6 = CricketTeamMemberFactory(team=team)
        member7 = CricketTeamMemberFactory(team=team)
        member8 = CricketTeamMemberFactory(team=team)
        member9 = CricketTeamMemberFactory(team=team)
        member10 = CricketTeamMemberFactory(team=team)
        member11 = CricketTeamMemberFactory(team=team)

        playing_eleven = [member1, member2, member3, member4, member5, member6, member7, member8, member9, member10, member11]

        match1 = CricketMatchFactory(team=team, playing_eleven=playing_eleven)
        match_stat1 = CricketMatchStatFactory(match=match1)
        match_stat2 = CricketMatchStatFactory(match=None)

        batting_stat1 = CricketMatchBattingStatFactory(match_stat=match_stat1, batsman=cricketer, runs=100, balls_played=30, fours=4, sixes=10)
        batting_stat2 = CricketMatchBattingStatFactory(match_stat=match_stat1, batsman=cricketer, runs=40, balls_played=30, fours=2, sixes=2)
        batting_stat3 = CricketMatchBattingStatFactory(match_stat=match_stat1, batsman=cricketer, runs=100, balls_played=20, fours=2, sixes=2)
        batting_stat4 = CricketMatchBattingStatFactory(match_stat=match_stat1, batsman=cricketer, runs=60, balls_played=30, dismissal_method='RH', fours=2, sixes=2)
        batting_stat5 = CricketMatchBattingStatFactory(match_stat=match_stat1, batsman=cricketer, runs=20, balls_played=30, dismissal_method='NO', fours=2, sixes=2)
        batting_stat6 = CricketMatchBattingStatFactory(match_stat=match_stat1, batsman=cricketer, runs=20, balls_played=30, fours=2, sixes=2)
        batting_stat7 = CricketMatchBattingStatFactory(match_stat=match_stat2, batsman=cricketer, runs=20, balls_played=30, dismissal_method='NO', fours=2, sixes=2)

        overall_batting_career_stats = user.get_overall_batting_career_stats(teams_only=True)

        self.assertEqual(overall_batting_career_stats['total_matches'], 6)
        self.assertEqual(overall_batting_career_stats['total_batting_innings'], 6)
        self.assertEqual(overall_batting_career_stats['not_out_innings_count'], 2)
        self.assertEqual(overall_batting_career_stats['total_runs'], 340)
        self.assertEqual(overall_batting_career_stats['total_balls_played'], 170)
        self.assertEqual(overall_batting_career_stats['fours'], 14)
        self.assertEqual(overall_batting_career_stats['sixes'], 20)
        self.assertEqual(overall_batting_career_stats['batting_average'], 85)
        self.assertEqual(overall_batting_career_stats['batting_strike_rate'], 200)
        self.assertEqual(overall_batting_career_stats['fifties'], 1)
        self.assertEqual(overall_batting_career_stats['hundreds'], 2)
        self.assertEqual(overall_batting_career_stats['highest_score'], 100)

    def test_get_overall_bowling_career_stats_returns_career_bowling_stats_in_teams(self):
        cricketer = CricketerFactory()
        user = cricketer.user
        team = CricketTeamFactory()

        member1 = CricketTeamMemberFactory(team=team, cricketer=cricketer, is_super_admin=True)
        member2 = CricketTeamMemberFactory(team=team)
        member3 = CricketTeamMemberFactory(team=team)
        member4 = CricketTeamMemberFactory(team=team)
        member5 = CricketTeamMemberFactory(team=team)
        member6 = CricketTeamMemberFactory(team=team)
        member7 = CricketTeamMemberFactory(team=team)
        member8 = CricketTeamMemberFactory(team=team)
        member9 = CricketTeamMemberFactory(team=team)
        member10 = CricketTeamMemberFactory(team=team)
        member11 = CricketTeamMemberFactory(team=team)

        playing_eleven = [member1, member2, member3, member4, member5, member6, member7, member8, member9, member10, member11]

        match1 = CricketMatchFactory(team=team, playing_eleven=playing_eleven)
        match_stat1 = CricketMatchStatFactory(match=match1)
        match_stat2 = CricketMatchStatFactory(match=None)

        bowling_stat1 = CricketMatchBowlingStatFactory(match_stat=match_stat1, bowler=cricketer, runs=100, wickets=5, overs=2)
        bowling_stat2 = CricketMatchBowlingStatFactory(match_stat=match_stat1, bowler=cricketer, runs=40, wickets=5, overs=2.4)
        bowling_stat3 = CricketMatchBowlingStatFactory(match_stat=match_stat1, bowler=cricketer, runs=80, wickets=3, overs=2.0)
        bowling_stat4 = CricketMatchBowlingStatFactory(match_stat=match_stat1, bowler=cricketer, runs=60, wickets=2, overs=1.0)
        bowling_stat5 = CricketMatchBowlingStatFactory(match_stat=match_stat1, bowler=cricketer, runs=20, wickets=5, overs=2.2)
        bowling_stat6 = CricketMatchBowlingStatFactory(match_stat=match_stat2, bowler=cricketer, runs=20, wickets=5, overs=2.2)

        overall_bowling_career_stats = user.get_overall_bowling_career_stats(teams_only=True)

        self.assertEqual(overall_bowling_career_stats['total_matches'], 5)
        self.assertEqual(overall_bowling_career_stats['total_balls_bowled'], 60)
        self.assertEqual(overall_bowling_career_stats['total_runs_conceded'], 300)
        self.assertEqual(overall_bowling_career_stats['total_wickets'], 20)
        self.assertEqual(overall_bowling_career_stats['economy'], 30)
        self.assertEqual(overall_bowling_career_stats['bowling_average'], 15)
        self.assertEqual(overall_bowling_career_stats['best_bowling_wickets'], 5)
        self.assertEqual(overall_bowling_career_stats['best_bowling_runs'], 20)


    def test_returns_false_in_latest_match_man_of_the_match_if_no_match(self):
        self.assertFalse(self.user.is_man_of_the_match_in_last_match())

    def test_returns_false_if_no_man_of_the_match_in_last_match(self):
        team = CricketTeamFactory()

        member1 = CricketTeamMemberFactory(team=team, cricketer=self.user.cricketer, is_super_admin=True)
        member2 = CricketTeamMemberFactory(team=team)
        member3 = CricketTeamMemberFactory(team=team)
        member4 = CricketTeamMemberFactory(team=team)
        member5 = CricketTeamMemberFactory(team=team)
        member6 = CricketTeamMemberFactory(team=team)
        member7 = CricketTeamMemberFactory(team=team)
        member8 = CricketTeamMemberFactory(team=team)
        member9 = CricketTeamMemberFactory(team=team)
        member10 = CricketTeamMemberFactory(team=team)
        member11 = CricketTeamMemberFactory(team=team)

        playing_eleven = [member1, member2, member3, member4, member5, member6, member7, member8, member9, member10, member11]

        match1 = CricketMatchFactory(team=team, playing_eleven=playing_eleven, man_of_the_match=None)
        match_stat1 = CricketMatchStatFactory(match=match1)

        match = CricketMatchFactory()
        self.assertFalse(self.user.is_man_of_the_match_in_last_match())

    def test_retuns_true_if_man_of_the_match_in_last_match(self):
        team = CricketTeamFactory()

        member1 = CricketTeamMemberFactory(team=team, cricketer=self.user.cricketer, is_super_admin=True)
        member2 = CricketTeamMemberFactory(team=team)
        member3 = CricketTeamMemberFactory(team=team)
        member4 = CricketTeamMemberFactory(team=team)
        member5 = CricketTeamMemberFactory(team=team)
        member6 = CricketTeamMemberFactory(team=team)
        member7 = CricketTeamMemberFactory(team=team)
        member8 = CricketTeamMemberFactory(team=team)
        member9 = CricketTeamMemberFactory(team=team)
        member10 = CricketTeamMemberFactory(team=team)
        member11 = CricketTeamMemberFactory(team=team)

        playing_eleven = [member1, member2, member3, member4, member5, member6, member7, member8, member9, member10, member11]

        match1 = CricketMatchFactory(team=team, playing_eleven=playing_eleven, man_of_the_match=member1)
        match_stat1 = CricketMatchStatFactory(match=match1)

        self.assertTrue(self.user.is_man_of_the_match_in_last_match())

    def test_get_all_teams_joined_returns_all_teams_joined(self):
        team1 = CricketTeamFactory()
        member1 = CricketTeamMemberFactory(team=team1, cricketer=self.user.cricketer)
        team2 = CricketTeamFactory()
        member2 = CricketTeamMemberFactory(team=team2, cricketer=self.user.cricketer)
        team3 = CricketTeamFactory()
        member3 = CricketTeamMemberFactory(team=team3, cricketer=self.user.cricketer)
        teams_joined = self.user.get_all_teams_joined()
        self.assertEqual(len(teams_joined), 3)
        self.assertIn(team1, teams_joined)
        self.assertIn(team2, teams_joined)
        self.assertIn(team3, teams_joined)

    def test_get_all_teams_joined_does_not_return_ex_teams(self):
        team1 = CricketTeamFactory()
        member1 = CricketTeamMemberFactory(team=team1, cricketer=self.user.cricketer)
        team2 = CricketTeamFactory()
        member2 = CricketTeamMemberFactory(team=team2, cricketer=self.user.cricketer, is_active=False)
        team3 = CricketTeamFactory()
        member3 = CricketTeamMemberFactory(team=team3, cricketer=self.user.cricketer, is_active=False)
        teams_joined = self.user.get_all_teams_joined()
        self.assertEqual(len(teams_joined), 1)
        self.assertIn(team1, teams_joined)
        self.assertNotIn(team2, teams_joined)
        self.assertNotIn(team3, teams_joined)

    def test_get_all_teams_joined_does_not_return_deleted_teams(self):
        team1 = CricketTeamFactory()
        member1 = CricketTeamMemberFactory(team=team1, cricketer=self.user.cricketer)
        team2 = CricketTeamFactory(is_deleted=True)
        member2 = CricketTeamMemberFactory(team=team2, cricketer=self.user.cricketer)
        team3 = CricketTeamFactory(is_deleted=True)
        member3 = CricketTeamMemberFactory(team=team3, cricketer=self.user.cricketer)
        teams_joined = self.user.get_all_teams_joined()
        self.assertEqual(len(teams_joined), 1)
        self.assertIn(team1, teams_joined)
        self.assertNotIn(team2, teams_joined)
        self.assertNotIn(team3, teams_joined)

    def test_get_all_teams_captaining_returns_all_teams_captaining(self):
        team1 = CricketTeamFactory()
        member1 = CricketTeamMemberFactory(team=team1, cricketer=self.user.cricketer, is_captain=True)
        team2 = CricketTeamFactory()
        member2 = CricketTeamMemberFactory(team=team2, cricketer=self.user.cricketer)
        team3 = CricketTeamFactory()
        member3 = CricketTeamMemberFactory(team=team3, cricketer=self.user.cricketer, is_captain=True)
        teams_captaining = self.user.get_all_teams_captaining()
        self.assertEqual(len(teams_captaining), 2)
        self.assertIn(team1, teams_captaining)
        self.assertNotIn(team2, teams_captaining)
        self.assertIn(team3, teams_captaining)

    def test_get_all_teams_captaining_returns_does_not_return_ex_captaining_teams(self):
        team1 = CricketTeamFactory()
        member1 = CricketTeamMemberFactory(team=team1, cricketer=self.user.cricketer, is_captain=True)
        team2 = CricketTeamFactory()
        member2 = CricketTeamMemberFactory(team=team2, cricketer=self.user.cricketer, is_captain=True, is_active=False)
        team3 = CricketTeamFactory()
        member3 = CricketTeamMemberFactory(team=team3, cricketer=self.user.cricketer, is_captain=True, is_active=False)
        teams_captaining = self.user.get_all_teams_joined()
        self.assertEqual(len(teams_captaining), 1)
        self.assertIn(team1, teams_captaining)
        self.assertNotIn(team2, teams_captaining)
        self.assertNotIn(team3, teams_captaining)

    def test_get_all_teams_captaining_returns_does_not_return_deleted_teams(self):
        team1 = CricketTeamFactory()
        member1 = CricketTeamMemberFactory(team=team1, cricketer=self.user.cricketer, is_captain=True)
        team2 = CricketTeamFactory(is_deleted=True)
        member2 = CricketTeamMemberFactory(team=team2, cricketer=self.user.cricketer, is_captain=True)
        team3 = CricketTeamFactory(is_deleted=True)
        member3 = CricketTeamMemberFactory(team=team3, cricketer=self.user.cricketer, is_captain=True)
        teams_captaining = self.user.get_all_teams_joined()
        self.assertEqual(len(teams_captaining), 1)
        self.assertIn(team1, teams_captaining)
        self.assertNotIn(team2, teams_captaining)
        self.assertNotIn(team3, teams_captaining)


@pytest.mark.django_db
class TestFriendRequest(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.friend_request = FriendRequestFactory()
        self.cricketer1 = CricketerFactory()
        self.cricketer2 = CricketerFactory()
        self.user1 = self.friend_request.from_user
        self.user2 = self.friend_request.to_user

    def test_instantiation(self):
        self.assertTrue(self.friend_request)

    def test_object_created(self):
        self.assertTrue(FriendRequest.objects.count())

    def test_cannot_create_same_friend_request_with_same_users(self):
        self.assertRaises(IntegrityError, FriendRequestFactory, from_user=self.user1, to_user=self.user2)

    def test_cannot_create_friend_request_with_same_from_and_to_user(self):
        self.assertRaises(ValidationError, FriendRequestFactory, from_user=self.user1, to_user=self.user1)

    def test_accepted_set_to_false_initially(self):
        self.assertFalse(self.friend_request.accepted)

    def test_viewed_set_to_false_initially(self):
        self.assertFalse(self.friend_request.viewed)

    def test_sent_on_field_set(self):
        self.assertTrue(self.friend_request.sent_on)

    def test_friend_added_when_request_accepted(self):
        self.assertEqual(self.user1.friends.all().count(), 0)
        self.friend_request.accept()
        self.assertEqual(self.user1.friends.all().count(), 1)
        self.assertTrue(self.user1.friends.filter(id=self.user2.id).exists())

    def test_friend_added_when_request_accepted_on_reverse_side_also(self):
        self.assertEqual(self.user2.friends.all().count(), 0)
        self.friend_request.accept()
        self.assertEqual(self.user2.friends.all().count(), 1)
        self.assertTrue(self.user2.friends.filter(id=self.user1.id).exists())

    def test_friend_requested_status_set_to_accepted(self):
        self.assertFalse(self.friend_request.accepted)
        self.friend_request.accept()
        self.assertTrue(self.friend_request.accepted)

    def test_reverse_friend_request_deleted_on_accept(self):
        friend_request2 = FriendRequestFactory(from_user=self.user2, to_user=self.user1)
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user2, to_user=self.user1).exists())
        self.friend_request.accept()
        self.assertFalse(FriendRequest.objects.filter(from_user=self.user2, to_user=self.user1).exists())

    def test_friend_request_deleted_on_reject(self):
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).exists())
        self.friend_request.reject()
        self.assertFalse(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).exists())

    def test_reverse_friend_request_deleted_on_reject(self):
        friend_request2 = FriendRequestFactory(from_user=self.user2, to_user=self.user1)
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user2, to_user=self.user1).exists())
        self.friend_request.reject()
        self.assertFalse(FriendRequest.objects.filter(from_user=self.user2, to_user=self.user1).exists())

    def test_friend_request_deleted_on_cancel(self):
        self.assertTrue(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).exists())
        self.friend_request.cancel()
        self.assertFalse(FriendRequest.objects.filter(from_user=self.user1, to_user=self.user2).exists())


@pytest.mark.django_db
class TestMessage(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.message = MessageFactory()
        self.sender = self.message.sender

    def test_instantiation(self):
        self.assertTrue(self.message)

    def test_object_created(self):
        self.assertTrue(Message.objects.count())

    def test_cannot_send_message_to_self(self):
        self.assertRaises(ValidationError, MessageFactory, sender=self.sender, recipient=self.sender)

    def test_unread_set_to_true(self):
        self.assertTrue(self.message.unread)

    def test_sent_on_date_set_automatically(self):
        self.assertTrue(self.message.sent_on)


@pytest.mark.django_db
class TestUserWallPost(unittest.TestCase):

    def setUp(self):
        self.user_wall_post = UserWallPostFactory()
        self.owner = self.user_wall_post.owner

    def test_instantiation(self):
        self.assertTrue(self.user_wall_post)

    def test_object_created(self):
        self.assertTrue(UserWallPost.objects.count())

    def test_posted_on_date_set_automatically(self):
        self.assertTrue(self.user_wall_post.posted_on)

    def test_user_wall_posts_results_sorted_by_latest_first(self):
        UserWallPost.objects.all().delete()
        user_wall_post1 = UserWallPostFactory()
        user_wall_post2 = UserWallPostFactory()
        user_wall_post3 = UserWallPostFactory()
        user_wall_post4 = UserWallPostFactory()
        user_wall_posts = UserWallPost.objects.all()
        self.assertEqual(list(user_wall_posts), [user_wall_post4, user_wall_post3, user_wall_post2, user_wall_post1])

    def test_user_wall_posts_results_sorted_even_after_filtering(self):
        user_wall_post2 = UserWallPostFactory(owner=self.owner)
        user_wall_post3 = UserWallPostFactory()
        user_wall_post4 = UserWallPostFactory(owner=self.owner)
        user_wall_post5 = UserWallPostFactory()
        user_wall_posts = UserWallPost.objects.filter(owner=self.owner)
        self.assertEqual(list(user_wall_posts), [user_wall_post4, user_wall_post2, self.user_wall_post])

    def test_user_wall_post_comments_sorted_with_oldest_first(self):
        user_wall_post_comment1 = UserWallPostCommentFactory(user_wall_post=self.user_wall_post)
        user_wall_post_comment2 = UserWallPostCommentFactory(user_wall_post=self.user_wall_post)
        user_wall_post_comment3 = UserWallPostCommentFactory(user_wall_post=self.user_wall_post)
        user_wall_post_comments = self.user_wall_post.user_wall_post_comments.all()
        self.assertEqual(list(user_wall_post_comments), [user_wall_post_comment1, user_wall_post_comment2, user_wall_post_comment3])


@pytest.mark.django_db
class TestUserWallPostComment(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.message = MessageFactory()
        self.sender = self.message.sender

    def test_instantiation(self):
        self.assertTrue(self.message)

    def test_object_created(self):
        self.assertTrue(Message.objects.count())

    def test_cannot_send_message_to_self(self):
        self.assertRaises(ValidationError, MessageFactory, sender=self.sender, recipient=self.sender)

    def test_unread_set_to_true(self):
        self.assertTrue(self.message.unread)

    def test_sent_on_date_set_automatically(self):
        self.assertTrue(self.message.sent_on)

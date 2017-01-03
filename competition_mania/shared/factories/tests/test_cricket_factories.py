# inbuilt python imports
import unittest
import os

# inbuilt django imports
from django.test import Client

# third-party django imports
import pytest

# inter-app imports
from accounts.models import User
from cricket.models import Cricketer, CricketTeam, CricketCertification, CricketTeamMember, CricketTeamWallPost, CricketTeamWallPostComment, CricketMatch, CricketMatchStat, CricketMatchBattingStat, CricketMatchBowlingStat, CricketTeamJoinRequest

# local imports
from sportsvitae.shared.factories.cricket_factories import CricketerFactory, BatsmanFactory, BowlerFactory, CricketTeamFactory, CricketCertificationFactory, CricketTeamMemberFactory, CricketTeamWallPostFactory, CricketTeamWallImagePostFactory, CricketTeamWallLocationPostFactory, CricketTeamWallPostCommentFactory, CricketMidoutMatchFactory, CricketMatchFactory, CricketMatchLostFactory, CricketMatchTiedFactory, CricketMatchDrawnFactory, CricketMatchNoResultFactory, CricketMidoutMatchStatFactory, CricketMatchStatFactory, CricketMatchBattingStatFactory, CricketMatchBowlingStatFactory, CricketTeamJoinRequestFactory


@pytest.mark.django_db
class TestCricketerFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.cricketer = CricketerFactory()

    def test_instantiation(self):
        self.assertTrue(self.cricketer)

    def test_object_created(self):
        self.assertEqual(Cricketer.objects.count(), 1)

    def test_user_also_created(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(self.cricketer.user)
        self.assertEqual(self.cricketer.user, User.objects.all()[0])

    def test_creates_another_cricketer_with_another_user(self):
        cricketer2 = CricketerFactory()
        self.assertEqual(Cricketer.objects.count(), 2)
        self.assertEqual(User.objects.count(), 2)

    def test_creates_another_cricketer_with_different_email(self):
        cricketer2 = CricketerFactory()
        self.assertEqual(Cricketer.objects.count(), 2)
        self.assertNotEqual(cricketer2.user.email, self.cricketer.user.email)

    def test_usp_set(self):
        self.assertEqual(self.cricketer.usp, 'BM')

    def test_best_performance_set(self):
        self.assertEqual(self.cricketer.profile_best_performance_display_type, 'BM')

    def test_usp_set_to_bowler_if_bowler_role(self):
        cricketer2 = CricketerFactory(role='BL')
        self.assertEqual(cricketer2.usp, 'BL')

    def test_usp_set_to_batsman_if_batsman_role(self):
        cricketer2 = CricketerFactory(role='BM')
        self.assertEqual(cricketer2.usp, 'BM')

    def test_usp_set_to_batsman_if_al_rounder_role(self):
        cricketer2 = CricketerFactory(role='AR')
        self.assertEqual(cricketer2.usp, 'BM')

    def test_best_performance_set_to_best_performance_if_bowler_role(self):
        cricketer2 = CricketerFactory(role='BL')
        self.assertEqual(cricketer2.profile_best_performance_display_type, 'BL')

    def test_best_performance_set_to_batsman_if_batsman_role(self):
        cricketer2 = CricketerFactory(role='BM')
        self.assertEqual(cricketer2.profile_best_performance_display_type, 'BM')

    def test_best_performance_set_to_batsman_if_al_rounder_role(self):
        cricketer2 = CricketerFactory(role='AR')
        self.assertEqual(cricketer2.profile_best_performance_display_type, 'BM')


@pytest.mark.django_db
class TestBatsmanFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.batsman = BatsmanFactory()

    def test_instantiation(self):
        self.assertTrue(self.batsman)

    def test_object_created(self):
        self.assertEqual(Cricketer.objects.count(), 1)

    def test_user_also_created(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(self.batsman.user)
        self.assertEqual(self.batsman.user, User.objects.all()[0])

    def test_creates_another_cricketer_with_another_user(self):
        batsman2 = CricketerFactory()
        self.assertEqual(Cricketer.objects.count(), 2)
        self.assertEqual(User.objects.count(), 2)

    def test_creates_another_cricketer_with_different_email(self):
        batsman2 = CricketerFactory()
        self.assertEqual(Cricketer.objects.count(), 2)
        self.assertNotEqual(batsman2.user.email, self.batsman.user.email)


@pytest.mark.django_db
class TestBowlerFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.bowler = BowlerFactory()

    def test_instantiation(self):
        self.assertTrue(self.bowler)

    def test_object_created(self):
        self.assertEqual(Cricketer.objects.count(), 1)

    def test_user_also_created(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(self.bowler.user)
        self.assertEqual(self.bowler.user, User.objects.all()[0])

    def test_creates_another_cricketer_with_another_user(self):
        bowler2 = CricketerFactory()
        self.assertEqual(Cricketer.objects.count(), 2)
        self.assertEqual(User.objects.count(), 2)

    def test_creates_another_cricketer_with_different_email(self):
        bowler2 = CricketerFactory()
        self.assertEqual(Cricketer.objects.count(), 2)
        self.assertNotEqual(bowler2.user.email, self.bowler.user.email)


@pytest.mark.django_db
class TestCricketTeamFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.cricket_team = CricketTeamFactory()

    def test_instantiation(self):
        self.assertTrue(self.cricket_team)

    def test_cricket_team_created(self):
        self.assertEqual(CricketTeam.objects.count(), 1)

    def test_cricketer_also_created(self):
        self.assertEqual(Cricketer.objects.count(), 1)
        self.assertTrue(self.cricket_team.super_admin)
        self.assertEqual(self.cricket_team.super_admin, Cricketer.objects.all()[0])

    def test_user_also_created(self):
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(self.cricket_team.super_admin.user)
        self.assertEqual(self.cricket_team.super_admin.user, User.objects.all()[0])

    def test_creates_another_cricket_team_with_another_cricketer(self):
        cricket_team2 = CricketTeamFactory()
        self.assertEqual(CricketTeam.objects.count(), 2)
        self.assertEqual(Cricketer.objects.count(), 2)
        self.assertEqual(User.objects.count(), 2)

    def test_creates_another_cricket_team_with_different_email(self):
        cricket_team2 = CricketTeamFactory()
        self.assertEqual(Cricketer.objects.count(), 2)
        self.assertNotEqual(cricket_team2.super_admin.user.email, self.cricket_team.super_admin.user.email)


@pytest.mark.django_db
class TestCricketCertificationFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.cricket_certification = CricketCertificationFactory()

    def test_instantiation(self):
        self.assertTrue(self.cricket_certification)

    def test_cricket_team_created(self):
        self.assertEqual(CricketCertification.objects.count(), 1)

    def test_cricketer_also_created(self):
        self.assertEqual(Cricketer.objects.count(), 1)

    def test_user_also_created(self):
        self.assertEqual(User.objects.count(), 1)

    def test_creates_another_cricket_team_with_another_cricketer(self):
        cricket_certification2 = CricketCertificationFactory()
        self.assertEqual(Cricketer.objects.count(), 2)
        self.assertEqual(User.objects.count(), 2)

    def test_creates_another_cricket_team_with_different_email(self):
        cricket_certification2 = CricketCertificationFactory()
        self.assertEqual(Cricketer.objects.count(), 2)
        self.assertNotEqual(cricket_certification2.cricketer.user.email, self.cricket_certification.cricketer.user.email)


@pytest.mark.django_db
class TestCricketTeamMemberFactory(unittest.TestCase):

    def setUp(self):
        self.cricket_team_member = CricketTeamMemberFactory()

    def test_instantiation(self):
        self.assertTrue(self.cricket_team_member)

    def test_cricket_team_member_created(self):
        self.assertEqual(CricketTeamMember.objects.count(), 1)

    def test_cricketer_also_created(self):
        self.assertTrue(Cricketer.objects.count())

    def test_user_also_created(self):
        self.assertTrue(User.objects.count(), 1)

    def test_cricket_team_created(self):
        self.assertEqual(CricketTeam.objects.count(), 1)

    def test_creates_2_cricketers(self):
        self.assertEqual(Cricketer.objects.count(), 2)

    def test_creates_2_users(self):
        self.assertEqual(User.objects.count(), 2)


@pytest.mark.django_db
class TestCricketTeamWallPostFactory(unittest.TestCase):

    def setUp(self):
        self.cricket_team_wall_post = CricketTeamWallPostFactory()
        self.posted_by = self.cricket_team_wall_post.posted_by

    def test_instantiation(self):
        self.assertTrue(self.cricket_team_wall_post)

    def test_object_created(self):
        self.assertTrue(CricketTeamWallPost.objects.count())

    def test_user_created(self):
        self.assertTrue(self.posted_by)
        self.assertEqual(User.objects.all().count(), 1)

    def test_likes_saved_correctly(self):
        self.assertFalse(self.cricket_team_wall_post.likes.count())
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        self.posted_by.add_friend(friend1)
        self.posted_by.add_friend(friend2)
        post2 = CricketTeamWallPostFactory(likes=[friend1, friend2])
        self.assertEqual(post2.likes.count(), 2)
        self.assertTrue(post2.likes.filter(id=friend1.id).exists())
        self.assertTrue(post2.likes.filter(id=friend2.id).exists())

    def test_location_is_none(self):
        self.assertIsNone(self.cricket_team_wall_post.location)

    def test_image_is_none(self):
        self.assertRaises(ValueError, getattr, self.cricket_team_wall_post.post_image, 'file')


@pytest.mark.django_db
class TestCricketTeamWallImagePostFactory(unittest.TestCase):

    def setUp(self):
        self.cricket_team_wall_image_post = CricketTeamWallImagePostFactory()
        self.posted_by = self.cricket_team_wall_image_post.posted_by

    def test_instantiation(self):
        self.assertTrue(self.cricket_team_wall_image_post)

    def test_object_created(self):
        self.assertTrue(CricketTeamWallPost.objects.count())

    def test_user_created(self):
        self.assertEqual(User.objects.all().count(), 1)

    def test_likes_saved_correctly(self):
        self.assertFalse(self.cricket_team_wall_image_post.likes.count())
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        self.posted_by.add_friend(friend1)
        self.posted_by.add_friend(friend2)
        post2 = CricketTeamWallImagePostFactory(likes=[friend1, friend2])
        self.assertEqual(post2.likes.count(), 2)
        self.assertTrue(post2.likes.filter(id=friend1.id).exists())
        self.assertTrue(post2.likes.filter(id=friend2.id).exists())

    def test_text_saved_correctly(self):
        self.assertEqual(self.cricket_team_wall_image_post.text, 'Check out this new pic')

    def test_post_type_saved_correctly(self):
        self.assertEqual(self.cricket_team_wall_image_post.post_type, 2)

    def test_post_image_saved_correctly(self):
        self.assertIsNotNone(self.cricket_team_wall_image_post.post_image.file)
        cricket_team_wall_post_image_path = self.cricket_team_wall_image_post.post_image.path
        self.assertTrue(os.path.exists(cricket_team_wall_post_image_path))

    def test_location_is_none(self):
        self.assertIsNone(self.cricket_team_wall_image_post.location)


@pytest.mark.django_db
class TestricketTeamWallLocationPostFactory(unittest.TestCase):

    def setUp(self):
        self.cricket_team_wall_location_post = CricketTeamWallLocationPostFactory()
        self.posted_by = self.cricket_team_wall_location_post.posted_by

    def test_instantiation(self):
        self.assertTrue(self.cricket_team_wall_location_post)

    def test_object_created(self):
        self.assertTrue(CricketTeamWallPost.objects.count())

    def test_user_created(self):
        self.assertEqual(User.objects.all().count(), 1)

    def test_likes_saved_correctly(self):
        self.assertFalse(self.cricket_team_wall_location_post.likes.count())
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        self.posted_by.add_friend(friend1)
        self.posted_by.add_friend(friend2)
        post2 = CricketTeamWallLocationPostFactory(likes=[friend1, friend2])
        self.assertEqual(post2.likes.count(), 2)
        self.assertTrue(post2.likes.filter(id=friend1.id).exists())
        self.assertTrue(post2.likes.filter(id=friend2.id).exists())

    def test_text_saved_correctly(self):
        self.assertEqual(self.cricket_team_wall_location_post.text, 'Checked in at')

    def test_post_type_saved_correctly(self):
        self.assertEqual(self.cricket_team_wall_location_post.post_type, 3)

    def test_location_saved_correctly(self):
        self.assertEqual(self.cricket_team_wall_location_post.location, 'Delhi, India')

    def test_image_is_none(self):
        self.assertRaises(ValueError, getattr, self.cricket_team_wall_location_post.post_image, 'file')


@pytest.mark.django_db
class TestricketTeamWallPostCommentFactory(unittest.TestCase):

    def setUp(self):
        self.cricket_team_wall_post_comment = CricketTeamWallPostCommentFactory()
        self.comment_by = self.cricket_team_wall_post_comment.comment_by
        self.cricket_team_wall_post = self.cricket_team_wall_post_comment.team_wall_post
        self.posted_by = self.cricket_team_wall_post.posted_by

    def test_instantiation(self):
        self.assertTrue(self.cricket_team_wall_post_comment)

    def test_object_created(self):
        self.assertTrue(CricketTeamWallPostComment.objects.count())

    def test_users_created(self):
        self.assertTrue(self.posted_by)
        self.assertTrue(self.comment_by)
        self.assertNotEqual(self.posted_by, self.comment_by)

    def test_user_wall_post_created(self):
        self.assertTrue(self.cricket_team_wall_post)
        self.assertEqual(CricketTeamWallPost.objects.all().count(), 1)

    def test_likes_saved_correctly(self):
        self.assertFalse(self.cricket_team_wall_post_comment.likes.count())
        friend1 = CricketerFactory().user
        friend2 = CricketerFactory().user
        self.posted_by.add_friend(friend1)
        self.posted_by.add_friend(friend2)
        post_comment2 = CricketTeamWallPostCommentFactory(likes=[friend1, friend2])
        self.assertEqual(post_comment2.likes.count(), 2)
        self.assertTrue(post_comment2.likes.filter(id=friend1.id).exists())
        self.assertTrue(post_comment2.likes.filter(id=friend2.id).exists())

    def test_non_friend_user_can_comment(self):
        self.assertFalse(self.posted_by.friends.filter(id=self.comment_by.id).exists())

    def test_friend_user_can_comment(self):
        friend1 = CricketerFactory().user
        self.posted_by.add_friend(friend1)
        cricket_team_wall_post = CricketTeamWallPostFactory(posted_by=self.posted_by)
        post_comment = CricketTeamWallPostCommentFactory(comment_by=friend1, team_wall_post=cricket_team_wall_post)
        self.assertTrue(post_comment)
        self.assertFalse(self.posted_by.friends.filter(id=self.comment_by.id).exists())


@pytest.mark.django_db
class TestCricketMidoutMatchFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.midout_match = CricketMidoutMatchFactory()

    def test_instantiation(self):
        self.assertTrue(self.midout_match)

    def test_object_created(self):
        self.assertEqual(CricketMatch.objects.count(), 1)

    def test_registration_midout_match(self):
        self.assertTrue(CricketMatch.objects.first().registration_midout)

    def test_team_also_created(self):
        self.assertEqual(CricketTeam.objects.count(), 1)
        self.assertEqual(self.midout_match.team, CricketTeam.objects.all()[0])


@pytest.mark.django_db
class TestCricketMatchFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.match = CricketMatchFactory()

    def test_instantiation(self):
        self.assertTrue(self.match)

    def test_object_created(self):
        self.assertEqual(CricketMatch.objects.count(), 1)

    def test_registration_midout_false_match(self):
        self.assertFalse(CricketMatch.objects.first().registration_midout)

    def test_win_result_set(self):
        self.assertEqual(CricketMatch.objects.first().result, 'W')

    def test_team_also_created(self):
        self.assertEqual(CricketTeam.objects.count(), 1)
        self.assertEqual(self.match.team, CricketTeam.objects.all()[0])


@pytest.mark.django_db
class TestCricketMatchLostFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.match = CricketMatchLostFactory()

    def test_instantiation(self):
        self.assertTrue(self.match)

    def test_object_created(self):
        self.assertEqual(CricketMatch.objects.count(), 1)

    def test_registration_midout_false_match(self):
        self.assertFalse(CricketMatch.objects.first().registration_midout)

    def test_loss_result_set(self):
        self.assertEqual(CricketMatch.objects.first().result, 'L')

    def test_team_also_created(self):
        self.assertEqual(CricketTeam.objects.count(), 1)
        self.assertEqual(self.match.team, CricketTeam.objects.all()[0])


@pytest.mark.django_db
class TestCricketMatchTiedFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.match = CricketMatchTiedFactory()

    def test_instantiation(self):
        self.assertTrue(self.match)

    def test_object_created(self):
        self.assertEqual(CricketMatch.objects.count(), 1)

    def test_registration_midout_false_match(self):
        self.assertFalse(CricketMatch.objects.first().registration_midout)

    def test_tied_result_set(self):
        self.assertEqual(CricketMatch.objects.first().result, 'T')

    def test_result_margin_not_set(self):
        self.assertFalse(CricketMatch.objects.first().result_margin)

    def test_result_margin_type_not_set(self):
        self.assertFalse(CricketMatch.objects.first().result_margin_type)

    def test_team_also_created(self):
        self.assertEqual(CricketTeam.objects.count(), 1)
        self.assertEqual(self.match.team, CricketTeam.objects.all()[0])


@pytest.mark.django_db
class TestCricketMatchDrawnFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.match = CricketMatchDrawnFactory()

    def test_instantiation(self):
        self.assertTrue(self.match)

    def test_object_created(self):
        self.assertEqual(CricketMatch.objects.count(), 1)

    def test_registration_midout_false_match(self):
        self.assertFalse(CricketMatch.objects.first().registration_midout)

    def test_drawn_result_set(self):
        self.assertEqual(CricketMatch.objects.first().result, 'D')

    def test_result_margin_not_set(self):
        self.assertFalse(CricketMatch.objects.first().result_margin)

    def test_result_margin_type_not_set(self):
        self.assertFalse(CricketMatch.objects.first().result_margin_type)

    def test_team_also_created(self):
        self.assertEqual(CricketTeam.objects.count(), 1)
        self.assertEqual(self.match.team, CricketTeam.objects.all()[0])


@pytest.mark.django_db
class TestCricketMatchNoResultFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.match = CricketMatchNoResultFactory()

    def test_instantiation(self):
        self.assertTrue(self.match)

    def test_object_created(self):
        self.assertEqual(CricketMatch.objects.count(), 1)

    def test_registration_midout_false_match(self):
        self.assertFalse(CricketMatch.objects.first().registration_midout)

    def test_drawn_result_set(self):
        self.assertEqual(CricketMatch.objects.first().result, 'N/R')

    def test_result_margin_not_set(self):
        self.assertFalse(CricketMatch.objects.first().result_margin)

    def test_result_margin_type_not_set(self):
        self.assertFalse(CricketMatch.objects.first().result_margin_type)

    def test_team_also_created(self):
        self.assertEqual(CricketTeam.objects.count(), 1)
        self.assertEqual(self.match.team, CricketTeam.objects.all()[0])


@pytest.mark.django_db
class TestCricketMidoutMatchStatFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.match_stat = CricketMidoutMatchStatFactory()

    def test_instantiation(self):
        self.assertTrue(self.match_stat)

    def test_object_created(self):
        self.assertEqual(CricketMatchStat.objects.count(), 1)

    def test_match_also_created(self):
        self.assertEqual(CricketMatch.objects.count(), 1)

    def test_registration_midout_set_for_match(self):
        self.assertTrue(CricketMatchStat.objects.first().match.registration_midout)

    def test_team_also_created(self):
        self.assertEqual(CricketTeam.objects.count(), 1)


@pytest.mark.django_db
class TestCricketMatchStatFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.match_stat = CricketMatchStatFactory()

    def test_instantiation(self):
        self.assertTrue(self.match_stat)

    def test_object_created(self):
        self.assertEqual(CricketMatchStat.objects.count(), 1)

    def test_match_also_created(self):
        self.assertEqual(CricketMatch.objects.count(), 1)

    def test_registration_midout_false_match(self):
        self.assertFalse(CricketMatchStat.objects.first().match.registration_midout)

    def test_team_also_created(self):
        self.assertEqual(CricketTeam.objects.count(), 1)



@pytest.mark.django_db
class TestCricketMatchBattingStatFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.batting_stat = CricketMatchBattingStatFactory()

    def test_instantiation(self):
        self.assertTrue(self.batting_stat)

    def test_object_created(self):
        self.assertEqual(CricketMatchBattingStat.objects.count(), 1)

    def test_match_stat_also_created(self):
        self.assertEqual(CricketMatchStat.objects.count(), 1)

    def test_match_also_created(self):
        self.assertEqual(CricketMatch.objects.count(), 1)

    def test_team_also_created(self):
        self.assertEqual(CricketTeam.objects.count(), 1)


@pytest.mark.django_db
class TestCricketMatchBowlingStatFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.bowling_stat = CricketMatchBowlingStatFactory()

    def test_instantiation(self):
        self.assertTrue(self.bowling_stat)

    def test_object_created(self):
        self.assertEqual(CricketMatchBowlingStat.objects.count(), 1)

    def test_match_stat_also_created(self):
        self.assertEqual(CricketMatchStat.objects.count(), 1)

    def test_match_also_created(self):
        self.assertEqual(CricketMatch.objects.count(), 1)

    def test_team_also_created(self):
        self.assertEqual(CricketTeam.objects.count(), 1)


@pytest.mark.django_db
class TestCricketTeamJoinRequestFactory(unittest.TestCase):

    def setUp(self):
        self.client = Client()
        self.cricket_team_join_request = CricketTeamJoinRequestFactory()

    def test_instantiation(self):
        self.assertTrue(self.cricket_team_join_request)

    def test_object_created(self):
        self.assertEqual(CricketTeamJoinRequest.objects.count(), 1)

    def test_cricketer_also_created(self):
        self.assertTrue(Cricketer.objects.count())

    def test_team_also_created(self):
        self.assertEqual(CricketTeam.objects.count(), 1)

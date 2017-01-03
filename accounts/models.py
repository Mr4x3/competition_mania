# Python Imports
import os
from collections import OrderedDict
from operator import itemgetter, attrgetter

# Django Imports
from django.template.defaultfilters import slugify
from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.db.models import Q, Max
from django.core.mail import send_mail
from django.template.loader import render_to_string

# Third Party Django Imports


# Inter App Imports
from lookup.choices import GENDER_CHOICES, COUNTRY_CHOICES, STATE_CHOICES, CITY_CHOICES, REGISTRATION_SOURCE_CHOICES, COUNTRY_CODE_MAPPING, USER_WALL_POST_TYPE_CHOICES, USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING
# from sportsvitae.shared.utils import prepare_name_and_id_slug
# from cricket.models import CricketMatchBattingStat, CricketMatchBowlingStat, CricketMatch, CricketMatchWicketKeepingStat, CricketTeam

# Local Imports
from .managers import UserManager
from .utils import get_first_and_last_name


def get_display_picture_path(instance, filename):
    return os.path.join(settings.IMAGE_UPLOAD_DIR_NAME, 'user_profiles', 'display_pictures', filename)


def get_cover_picture_path(instance, filename):
    return os.path.join(settings.IMAGE_UPLOAD_DIR_NAME, 'user_profiles', 'cover_pictures', filename)


def get_user_wall_post_picture_path(instance, filename):
    return os.path.join(settings.IMAGE_UPLOAD_DIR_NAME, 'user_wall_posts', 'pictures', filename)


def get_user_notification_display_picture_path(instance, filename):
    return os.path.join(settings.IMAGE_UPLOAD_DIR_NAME, 'user_notifications', 'display_pictures', filename)

def prepare_name_and_id_slug(name, object_id):
    slug_string = '{} {}'.format(name, object_id)
    slug = slugify(slug_string)
    return slug

class Message(models.Model):
    """"
    Model For Handling Messages Between Users.
    """
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages_sent')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages_received')
    sent_on = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    unread = models.BooleanField(default=True)
    deleted_by_sender = models.BooleanField(default=False)  # Flag to Check If Chat History Deleted
    deleted_by_recipient = models.BooleanField(default=False)  # Flag to Check If Chat History Deleted

    def __str__(self):
        return self.text

    def save(self, *args, **kwargs):
        if self.sender == self.recipient:
            raise ValidationError('Cannot send message to ourselves.')
        super(Message, self).save(*args, **kwargs)


class User(AbstractBaseUser):
    """
    Custom User Profile model
    """

    friends = models.ManyToManyField("self", blank=True)
    email = models.EmailField(max_length=255, unique=True)  # Primary Key
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    gender = models.CharField(default='M', choices=GENDER_CHOICES, max_length=1)
    mobile = models.CharField(blank=True, max_length=10)
    country = models.CharField(default='IN', choices=COUNTRY_CHOICES, max_length=2)
    state = models.IntegerField(blank=True, null=True, choices=STATE_CHOICES)
    state_text = models.CharField(blank=True, max_length=30)
    city = models.IntegerField(blank=True, null=True, choices=CITY_CHOICES)
    city_text = models.CharField(blank=True, max_length=30)
    date_of_birth = models.DateTimeField(blank=True, null=True)
    display_picture = models.ImageField(blank=True, null=True, upload_to=get_display_picture_path)
    cover_picture = models.ImageField(blank=True, null=True, upload_to=get_cover_picture_path)
    created_on = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    registration_source = models.IntegerField(default=1, choices=REGISTRATION_SOURCE_CHOICES)
    registration_midout = models.BooleanField(default=True)
    is_email_verified = models.BooleanField(default=False)
    slug = models.SlugField(max_length=70, blank=True, unique=False)
    social_profile_id = models.CharField(max_length=40, blank=True, null=True, unique=True)
    tour_completed = models.BooleanField(default=True)  # Front Works Other Way So.
    last_profile_complation_mail = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'user'
        ordering = ['first_name']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        """
        Does the User Have a Specific Permission?
        """
        return self.is_staff

    def has_module_perms(self, app_label):
        """
        Does the User Have Permissions to View the App `App_label`?
        """
        return self.is_staff

    def get_full_name(self):
        return '{} {}'.format(self.first_name.title(), self.last_name.title())

    def get_short_name(self):
        return self.first_name

    def is_registration_midout(self):
        return self.registration_midout

    # def has_sports_profile(self):
    #     from cricket.models import Cricketer
    #     try:
    #         cricketer = self.cricketer
    #         return True
    #     except Cricketer.DoesNotExist:
    #         return False

    # def is_complete_user(self):
    #     """
    #     Returns True If User Has Done Profile Specific Registration And Created
    #     a Sports Profile.
    #     """
    #     return self.is_email_verified and not self.is_registration_midout() and self.has_sports_profile()

    # @property
    # def full_name(self):
    #     return self.get_full_name()

    # @property
    # def name(self):
    #     return self.get_full_name()

    # @name.setter
    # def name(self, full_name):
    #     first_name, last_name = get_first_and_last_name(full_name)
    #     self.first_name, self.last_name = first_name, last_name

    # @property
    # def country_code(self):
    #     return COUNTRY_CODE_MAPPING[self.country]

    # def get_state_display_value(self):
    #     if self.state:
    #         return self.get_state_display()
    #     return self.state_text

    # def get_city_display_value(self):
    #     if self.city:
    #         return self.get_city_display()
    #     return self.city_text

    # def from_india(self):
    #     """
    #     Returns True For Non-indian User
    #     """
    #     return self.country == 'IN'

    # def is_foreigner(self):
    #     """
    #     Returns True For Non-indian User
    #     """
    #     return self.country != 'IN'

    # def create_slug(self):
    #     """
    #     Creates a New Slug Using Name And Id
    #     """
    #     self.slug = prepare_name_and_id_slug(self.name, self.id)
    #     self.save()

    # def update_slug(self):
    #     """
    #     Updates the Slug If Name Is Changed
    #     """
    #     user_slug = prepare_name_and_id_slug(self.name, self.id)
    #     if self.slug != user_slug:
    #         self.slug = user_slug

    # def add_friend(self, friend):
    #     if friend == self:
    #         raise ValidationError("Users cannot be friends with themselves.")

    #     if not self.is_complete_user():
    #         raise ValidationError("Only fully registered users can add friends.")

    #     if not friend.is_complete_user():
    #         raise ValidationError("Only fully registered users can be added as friends.")

    #     self.friends.add(friend)  # Add Friend

    # def remove_friend(self, friend):
    #     if friend == self:
    #         raise ValidationError("Users cannot be friends with themselves.")

    #     self.friends.remove(friend)  # Remove Friend

    # def get_friend_suggestions(self):
    #     """
    #     Returns Friend Suggestions Based On the City Where User Lives.
    #     """
    #     user_model = get_user_model()

    #     # Get All Users Having Same City
    #     if self.from_india():
    #         friend_suggestions = user_model.objects.filter(city=self.city)
    #     else:
    #         friend_suggestions = user_model.objects.filter(city_text=self.city_text)

    #     # Exclude Current Friends And Self
    #     friend_ids = self.friends.all().values_list('id', flat=True)
    #     friend_requests_sent_friend_ids = FriendRequest.objects.filter(from_user=self).values_list('to_user', flat=True)
    #     exclude_ids = list(friend_ids) + [self.id] + list(friend_requests_sent_friend_ids)
    #     friend_suggestions = friend_suggestions.exclude(id__in=exclude_ids)

    #     return friend_suggestions

    # def get_team_follow_suggestions(self):
    #     """
    #     Returns Team Follow Suggestions Based On the Team Friends Have Joined.
    #     """

    #     if not self.is_complete_user():
    #         return []

    #     user_model = get_user_model()
    #     friend_ids = set()  # Define an Empty Set
    #     all_friends = user_model.objects.filter(id=self.id).values_list('friends', 'friends__friends') # Level 1+2 friends
    #     level_1_friends = [x[0] for x in all_friends]  # Level -1 Friends
    #     level_2_friends = [x[1] for x in all_friends]  # Level -2 Friends
    #     friend_ids.update(level_1_friends + level_2_friends)  # Get Unique Friends

    #     if self.id in friend_ids:
    #         friend_ids.remove(self.id)  # Remove Own Id

    #     # Exclude Already Following Teams
    #     teams_following_ids = list(self.cricketer.teams_following.all().values_list('id', flat=True))

    #     team_follow_suggestions = CricketTeam.objects.filter(is_deleted=False, team_members__is_active=True).filter(team_members__cricketer__user__in=friend_ids).exclude(team_members__cricketer__user=self).exclude(id__in=teams_following_ids).distinct()
    #     return team_follow_suggestions

    # def get_all_friends_messaged(self):
    #     friends_messaged_ids_mapping = OrderedDict()

    #     friends_messaged = Message.objects.filter(Q(sender=self, deleted_by_sender=False) | Q(recipient=self, deleted_by_recipient=False)).order_by('-sent_on').values_list('sender_id', 'recipient_id')

    #     for sender_id, recipient_id in friends_messaged:
    #         friend_id = sender_id if sender_id != self.id else recipient_id
    #         if friend_id not in friends_messaged_ids_mapping:
    #             friends_messaged_ids_mapping[friend_id] = friend_id

    #     all_friends_messaged = self.friends.filter(id__in=friends_messaged_ids_mapping.keys())
    #     for friend in all_friends_messaged:
    #         friends_messaged_ids_mapping[friend.id] = friend

    #     return list(friends_messaged_ids_mapping.values())

    # def get_last_messaged_friend_messages(self):
    #     last_message = list(Message.objects.filter(Q(sender=self, deleted_by_sender=False) | Q(recipient=self, deleted_by_recipient=False)).order_by('-sent_on'))
    #     if not last_message:
    #         return []
    #     last_message = last_message[0]

    #     last_messaged_friend_id = last_message.sender_id if last_message.sender_id != self.id else last_message.recipient_id
    #     last_messaged_friend_messages = Message.objects.filter(Q(sender=self, recipient_id=last_messaged_friend_id, deleted_by_sender=False) | Q(sender_id=last_messaged_friend_id, recipient=self, deleted_by_recipient=False)).order_by('sent_on')
    #     return last_messaged_friend_messages

    # def get_chat_between_friend(self, friend):
    #     """
    #     Returns Messages with a Particular Friend.
    #     """
    #     return Message.objects.filter(Q(sender=self, recipient=friend, deleted_by_sender=False)|Q(sender=friend, recipient=self, deleted_by_recipient=False)).order_by('sent_on')

    # def get_all_friend_requests(self):
    #     """
    #     Returns Friend Requests Sorted By Viewed(not Viewed First) Flag
    #     And Then By Time(latest First)
    #     """
    #     return list(FriendRequest.objects.filter(to_user=self, accepted=False).order_by('viewed', '-sent_on'))

    # def get_latest_friend_requests(self):
    #     """
    #     Returns Latest 3 Friend Requests
    #     """
    #     all_friend_requests = self.get_all_friend_requests()
    #     return all_friend_requests[:3]

    # def get_latest_received_messages(self):
    #     """
    #     Returns Latest Received Messages By Last 3 Senders
    #     """
    #     sender_ids = list(Message.objects.filter(recipient=self, deleted_by_recipient=False).values_list('sender', flat=True).distinct())

    #     if not sender_ids:
    #         return []

    #     latest_sender_messages = Message.objects.filter(sender__in=sender_ids, recipient=self, deleted_by_recipient=False).order_by('-unread', '-sent_on')
    #     latest_received_messages_mapping = OrderedDict()
    #     for message in latest_sender_messages:
    #         if message.sender_id not in latest_received_messages_mapping:
    #             latest_received_messages_mapping[message.sender_id] = message

    #     latest_received_messages = list(latest_received_messages_mapping.values())

    #     return latest_received_messages[:3]

    # def get_all_user_notifications(self):
    #     return list(UserNotification.objects.filter(user=self).order_by('viewed', '-created_on'))

    # def get_latest_user_notifications(self):
    #     """
    #     Returns Latest 3 User Notifications.
    #     """
    #     all_user_notifications = self.get_all_user_notifications()
    #     return all_user_notifications[:3]

    # def get_all_user_posts_for_user_wall(self):
    #     friends_ids = list(self.friends.all().values_list('id', flat=True))
    #     eligible_post_owners_ids = [self.id] + friends_ids
    #     user_wall_posts = list(UserWallPost.objects.filter(owner_id__in=eligible_post_owners_ids).order_by('-posted_on').prefetch_related('likes', 'user_wall_post_comments'))
    #     return user_wall_posts

    # def get_all_cricket_team_posts_for_user_wall(self):
    #     from cricket.models import CricketTeamWallPost

    #     if not self.is_complete_user():
    #         return []

    #     teams_following_ids = list(self.cricketer.teams_following.all().values_list('id', flat=True))

    #     cricket_team_posts = list(CricketTeamWallPost.objects.filter(team__is_deleted=False, team__team_members__is_active=True).filter(Q(team__team_members__cricketer__user=self)|Q(team__id__in=teams_following_ids)).prefetch_related('likes', 'cricket_team_wall_post_comments').distinct())

    #     return cricket_team_posts

    # def get_all_user_wall_posts(self):
    #     """
    #     Returns All User Wall Posts (Self & Friends) Sorted By Latest First.
    #     """

    #     user_posts = self.get_all_user_posts_for_user_wall()
    #     cricket_team_posts = self.get_all_cricket_team_posts_for_user_wall()

    #     all_user_wall_posts = user_posts + cricket_team_posts

    #     all_user_wall_posts.sort(key=attrgetter('posted_on'), reverse=True)
    #     return all_user_wall_posts

    # def get_all_teams_joined(self):
    #     from cricket.models import CricketTeam, CricketTeamMember

    #     teams_joined_ids = list(CricketTeamMember.objects.filter(team__is_deleted=False, is_active=True, cricketer__user=self).values_list('team', flat=True))
    #     teams_joined = CricketTeam.objects.filter(id__in=teams_joined_ids)

    #     return teams_joined

    # def get_all_teams_captaining(self):
    #     from cricket.models import CricketTeam, CricketTeamMember

    #     teams_captaining_ids = list(CricketTeamMember.objects.filter(team__is_deleted=False, is_active=True, cricketer__user=self, is_captain=True).values_list('team', flat=True))
    #     teams_captaining = CricketTeam.objects.filter(id__in=teams_captaining_ids)

    #     return teams_captaining

    # def get_best_batting_performance(self):
    #     from cricket.models import CricketMatchBattingStat
    #     batting_stats = list(CricketMatchBattingStat.objects.filter(batsman__user_id=self.id))
    #     if not batting_stats:
    #         return {}

    #     highest_score_runs = max(x.runs for x in batting_stats)

    #     best_batting_performance = {
    #         'highest_score_runs': highest_score_runs,
    #         'highest_score_balls_played': min(x.balls_played for x in batting_stats if x.runs==highest_score_runs),
    #         'max_fours': max(batting_stats, key=attrgetter('fours')).fours,
    #         'max_sixes': max(batting_stats, key=attrgetter('sixes')).sixes,
    #         'fifties': sum(49 < x.runs < 100 for x in batting_stats),
    #         'hundreds': sum(x.runs > 99 for x in batting_stats)
    #     }
    #     return best_batting_performance

    # def get_best_bowling_performance(self):
    #     from cricket.models import CricketMatchBowlingStat
    #     bowling_stats = list(CricketMatchBowlingStat.objects.filter(bowler__user_id=self.id))
    #     if not bowling_stats:
    #         return {}

    #     best_bowling_wickets = max(x.wickets for x in bowling_stats)
    #     best_bowling_runs_list = [x.runs for x in bowling_stats if x.wickets == best_bowling_wickets]
    #     best_bowling_runs = min(best_bowling_runs_list) if best_bowling_runs_list else 0

    #     best_bowling_performance = {
    #         'best_bowling_wickets': best_bowling_wickets,
    #         'best_bowling_runs': best_bowling_runs,
    #         'three_wicket_hauls': sum(x.wickets >= 3 for x in bowling_stats),
    #         'five_wicket_hauls': sum(x.wickets >= 5 for x in bowling_stats)
    #     }
    #     return best_bowling_performance

    # def get_best_performance_stats(self):
    #     best_batting_performance = self.get_best_batting_performance()
    #     best_bowling_performance = self.get_best_bowling_performance()
    #     best_performance_stats = dict(best_batting_performance, **best_bowling_performance)
    #     return best_performance_stats

    # def get_overall_batting_career_stats(self, teams_only=False):
    #     from cricket.models import CricketMatchBattingStat, CricketMatchBowlingStat, CricketMatch
    #     if teams_only:
    #         batting_stats = list(CricketMatchBattingStat.objects.filter(match_stat__match__playing_eleven__cricketer__user_id=self.id).filter(batsman__user_id=self.id))
    #     else:
    #         batting_stats = list(CricketMatchBattingStat.objects.filter(batsman__user_id=self.id))

    #     match_stat_ids = [x.match_stat_id for x in batting_stats]

    #     if teams_only:
    #         matches_did_not_bat_count = CricketMatch.objects.exclude(match_stat__id__in=match_stat_ids).filter(playing_eleven__cricketer__user_id=self.id).count()
    #     else:
    #         team_matches_did_not_bat_count = CricketMatch.objects.exclude(match_stat__id__in=match_stat_ids).filter(playing_eleven__cricketer__user_id=self.id).count()

    #         user_matches_bowled_ids = set(CricketMatchBowlingStat.objects.filter(match_stat__match__isnull=True, bowler__user_id=self.id).values_list('match_stat', flat=True).distinct())
    #         user_matches_batted_ids = set(CricketMatchBattingStat.objects.filter(match_stat__match__isnull=True, batsman__user_id=self.id).values_list('match_stat', flat=True).distinct())
    #         user_matches_did_not_bat_count = len(user_matches_bowled_ids - user_matches_batted_ids)

    #         matches_did_not_bat_count = team_matches_did_not_bat_count + user_matches_did_not_bat_count

    #     if not batting_stats and not matches_did_not_bat_count:
    #         return {}

    #     total_batting_innings = len(batting_stats)
    #     not_out_innings_count = sum(x.is_not_out() for x in batting_stats)
    #     out_innings_count = total_batting_innings - not_out_innings_count

    #     total_batting_innings_before_last_match = len(batting_stats[:-1])
    #     not_out_innings_count_before_last_match = sum(x.is_not_out() for x in batting_stats[:-1])
    #     out_innings_count_before_last_match = total_batting_innings_before_last_match - not_out_innings_count_before_last_match

    #     total_runs = sum(x.runs for x in batting_stats)
    #     total_runs_before_last_match = sum(x.runs for x in batting_stats[:-1])

    #     total_balls_played = sum(x.balls_played for x in batting_stats)
    #     total_balls_played_before_last_match = sum(x.balls_played for x in batting_stats[:-1])

    #     overall_batting_career_stats = {
    #         'total_matches': total_batting_innings + matches_did_not_bat_count,
    #         'total_batting_innings': total_batting_innings,
    #         'not_out_innings_count': not_out_innings_count,
    #         'total_runs': total_runs,
    #         'total_balls_played': total_balls_played,
    #         'fours': sum(x.fours for x in batting_stats),
    #         'sixes': sum(x.sixes for x in batting_stats),
    #         'batting_average': [round(total_runs_before_last_match/out_innings_count_before_last_match, 1) if out_innings_count_before_last_match>0 else total_runs_before_last_match, round(total_runs/out_innings_count, 1) if out_innings_count>0 else total_runs],
    #         'batting_strike_rate': [round(100*(total_runs_before_last_match/total_balls_played_before_last_match), 1) if total_balls_played_before_last_match > 0 else 0, round(100*(total_runs/total_balls_played), 1) if total_balls_played > 0 else 0],
    #         'fifties': sum(49 < x.runs < 100 for x in batting_stats),
    #         'hundreds': sum(x.runs > 99 for x in batting_stats),
    #         'highest_score': max(x.runs for x in batting_stats) if batting_stats else 0
    #     }
    #     return overall_batting_career_stats

    # def get_overall_bowling_career_stats(self, teams_only=False):
    #     from cricket.models import CricketMatchBowlingStat, CricketMatch

    #     if teams_only:
    #         bowling_stats = list(CricketMatchBowlingStat.objects.filter(match_stat__match__playing_eleven__cricketer__user_id=self.id).filter(bowler__user_id=self.id))
    #     else:
    #         bowling_stats = list(CricketMatchBowlingStat.objects.filter(bowler__user_id=self.id))

    #     match_stat_ids = [x.match_stat_id for x in bowling_stats]

    #     matches_did_not_bowl_count = CricketMatch.objects.exclude(match_stat__id__in=match_stat_ids).filter(playing_eleven__cricketer__user_id=self.id).count()

    #     if not bowling_stats and not matches_did_not_bowl_count:
    #         return {}

    #     total_runs_conceded = sum(x.runs for x in bowling_stats)
    #     total_runs_conceded_before_last_match = sum(x.runs for x in bowling_stats[:-1])

    #     total_balls_bowled = sum(x.balls_bowled for x in bowling_stats)
    #     total_balls_bowled_before_last_match = sum(x.balls_bowled for x in bowling_stats[:-1])

    #     total_wickets = sum(x.wickets for x in bowling_stats)
    #     total_wickets_before_last_match = sum(x.wickets for x in bowling_stats[:-1])

    #     best_bowling_wickets = max(x.wickets for x in bowling_stats) if bowling_stats else 0
    #     # best_bowling_wickets_before_last_match = max(x.wickets for x in bowling_stats[:-1]) if bowling_stats[:-1] else 0

    #     best_bowling_runs_list = [x.runs for x in bowling_stats if x.wickets==best_bowling_wickets]
    #     # best_bowling_runs_list_before_last_match = [x.runs for x in bowling_stats[:-1] if x.wickets==best_bowling_wickets[:-1]]

    #     best_bowling_runs = min(best_bowling_runs_list) if best_bowling_runs_list else 0
    #     # best_bowling_runs_before_last_match = min(best_bowling_runs_list[:-1]) if best_bowling_runs_list[:-1] else 0

    #     overall_bowling_career_stats = {
    #         'total_matches': len(bowling_stats) + matches_did_not_bowl_count,
    #         'total_balls_bowled': total_balls_bowled,
    #         'total_runs_conceded': total_runs_conceded,
    #         'total_wickets': total_wickets,
    #         'economy': [round(total_runs_conceded_before_last_match/(total_balls_bowled_before_last_match/6), 1) if total_balls_bowled_before_last_match > 0 else 0, round(total_runs_conceded/(total_balls_bowled/6), 1) if total_balls_bowled > 0 else 0],
    #         'bowling_average': [round(total_runs_conceded_before_last_match/total_wickets_before_last_match, 1) if total_wickets_before_last_match else 0, round(total_runs_conceded/total_wickets, 1) if total_wickets else 0],
    #         'best_bowling_runs': best_bowling_runs,
    #         'best_bowling_wickets': best_bowling_wickets
    #     }

    #     return overall_bowling_career_stats

    # def get_overall_wicket_keeping_career_stats(self, teams_only=False):
    #     if teams_only:
    #         wicketkeeper_stats = list(CricketMatchWicketKeepingStat.objects.filter(match_stat__match__playing_eleven__cricketer__user_id=self.id).filter(wicketkeeper__user_id=self.id))
    #     else:
    #         wicketkeeper_stats = list(CricketMatchWicketKeepingStat.objects.filter(wicketkeeper__user_id=self.id))

    #     match_stat_ids = [x.match_stat_id for x in wicketkeeper_stats]

    #     if teams_only:
    #         matches_did_not_wicketkeep_count = CricketMatch.objects.exclude(match_stat__id__in=match_stat_ids).filter(playing_eleven__cricketer__user_id=self.id).count()
    #     else:
    #         team_matches_did_not_wicketkeep_count = CricketMatch.objects.exclude(match_stat__id__in=match_stat_ids).filter(playing_eleven__cricketer__user_id=self.id).count()

    #         # user_matches_bowled_ids = set(CricketMatchBowlingStat.objects.filter(match_stat__match__isnull=True, bowler__user_id=self.id).values_list('match_stat', flat=True).distinct())
    #         # user_matches_batted_ids = set(CricketMatchBattingStat.objects.filter(match_stat__match__isnull=True, batsman__user_id=self.id).values_list('match_stat', flat=True).distinct())
    #         # user_matches_did_not_bat_count = len(user_matches_bowled_ids - user_matches_batted_ids)
    #         #
    #         matches_did_not_wicketkeep_count = team_matches_did_not_wicketkeep_count  # + user_matches_did_not_bat_count

    #     if not wicketkeeper_stats and not matches_did_not_wicketkeep_count:
    #         return {}

    #     total_wicketkeeper_innings = len(wicketkeeper_stats)
    #     total_wicketkeeper_matches = total_wicketkeeper_innings + matches_did_not_wicketkeep_count
    #     total_stumps = sum(x.stumps for x in wicketkeeper_stats)
    #     total_catches = sum(x.catches for x in wicketkeeper_stats)
    #     total_run_out = sum(x.run_out for x in wicketkeeper_stats)

    #     overall_batting_career_stats = {
    #         'total_wicketkeeper_innings': total_wicketkeeper_innings,
    #         'total_wicketkeeper_matches': total_wicketkeeper_matches,
    #         'total_stumps': total_stumps,
    #         'total_catches': total_catches,
    #         'total_run_out': total_run_out,
    #     }
    #     return overall_batting_career_stats

    # def is_man_of_the_match_in_last_match(self):
    #     from cricket.models import CricketMatch
    #     last_cricket_match_played = CricketMatch.objects.filter(playing_eleven__cricketer__user_id=self.id, registration_midout=False).order_by('-match_stat__match_date').first()

    #     if last_cricket_match_played and last_cricket_match_played.man_of_the_match and last_cricket_match_played.man_of_the_match.cricketer.user_id == self.id:
    #         return True

    #     return False

    # def save(self, *args, **kwargs):
    #     if self.id:
    #         self.update_slug()
    #     super(User, self).save(*args, **kwargs)
    #     if not self.slug:
    #         self.create_slug()


# class FriendRequest(models.Model):
#     """
#     Model for storing Connect Requests.
#     """
#     from_user = models.ForeignKey(User, related_name='friend_requests_sent')
#     to_user = models.ForeignKey(User, related_name='friend_requests_received')
#     accepted = models.BooleanField(default=False)
#     viewed = models.BooleanField(default=False)
#     sent_on = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         unique_together = (('from_user', 'to_user'),)

#     def accept(self):
#         """
#         Accept a friend request.
#         """
#         self.from_user.add_friend(friend=self.to_user)  # Add Friend
#         self.accepted = True  # Change Friend Request Status
#         self.save()

#         # Delete Reverse Requests
#         FriendRequest.objects.filter(from_user=self.to_user, to_user=self.from_user).delete()

#     def reject(self):
#         """
#         Reject a friend request.
#         """
#         self.delete()  # Delete Friend Request

#         # Delete Any Reverse Requests
#         FriendRequest.objects.filter(from_user=self.to_user, to_user=self.from_user).delete()

#     def cancel(self):
#         """
#         Cancel a friend request.
#         """
#         self.delete()  # Delete Friend Request

#     def save(self, *args, **kwargs):
#         if self.from_user == self.to_user:
#             raise ValidationError('One cannot send friend request to himself.')
#         super(FriendRequest, self).save(*args, **kwargs)


# class UserWallPost(models.Model):
#     """"
#     Model For Handling Posts Posted By a User On His Wall.
#     """
#     owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_wall_posts')
#     likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='user_wall_posts_liked')
#     text = models.TextField(blank=True, null=True)
#     post_image = models.ImageField(blank=True, null=True, upload_to=get_user_wall_post_picture_path)
#     location = models.TextField(blank=True, null=True)
#     post_type = models.IntegerField(choices=USER_WALL_POST_TYPE_CHOICES, default=1)
#     posted_on = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-posted_on']

#     def __str__(self):
#         return self.text


# class UserWallPostComment(models.Model):
#     """
#     Model For Handling Comments On the Posts Posted By a User On His Wall.
#     """
#     comment_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_wall_posts_commented_on')
#     user_wall_post = models.ForeignKey(UserWallPost , related_name='user_wall_post_comments')
#     comment = models.TextField()
#     likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='user_wall_post_comments_liked')
#     commented_on = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['commented_on']

#     def __str__(self):
#         return self.comment


# class UserNotification(models.Model):

#     ACCEPT_FRIEND_REQUEST = 1
#     ADD_CRICKET_TEAM = 2
#     ADD_CAPTAIN_CRICKET_TEAM = 3
#     ADD_VICE_CAPTAIN_CRICKET_TEAM = 4
#     ADD_NEW_CRICKET_MATCH = 5
#     ADD_NEW_CRICKET_MATCH_SCORE_SHEET = 6
#     CRICKET_MATCH_MAN_OF_THE_MATCH = 7
#     CRICKET_MATCH_BEST_BATSMAN = 8
#     CRICKET_MATCH_BEST_BOWLER = 9
#     CRICKET_MATCH_BEST_FIELDER = 10
#     FOLLOW_CRICKET_TEAM = 11
#     CRICKET_TEAM_INVITE = 12
#     POST_FRIEND_COMMENT = 13
#     POST_FRIEND_LIKE = 14
#     TEAM_MEMBER_VACANCY = 15

#     NOTIFICATION_TYPE_CHOICES = (
#         (ACCEPT_FRIEND_REQUEST, 'Accept Friend Request'),
#         (ADD_CRICKET_TEAM, 'Add Cricket Team'),
#         (ADD_CAPTAIN_CRICKET_TEAM, 'Captain Cricket Team'),
#         (ADD_VICE_CAPTAIN_CRICKET_TEAM, 'Vice Captain Cricket Team'),
#         (ADD_NEW_CRICKET_MATCH, 'Add Cricket Match'),
#         (ADD_NEW_CRICKET_MATCH_SCORE_SHEET, 'Add Cricket Match Score Sheet'),
#         (CRICKET_MATCH_MAN_OF_THE_MATCH, 'Man Of The Match'),
#         (CRICKET_MATCH_BEST_BATSMAN, 'Best Batsman'),
#         (CRICKET_MATCH_BEST_BOWLER, 'Best Bowler'),
#         (CRICKET_MATCH_BEST_FIELDER, 'Best Fielder'),
#         (FOLLOW_CRICKET_TEAM, 'Follow Cricket Team'),
#         (CRICKET_TEAM_INVITE, 'Cricket Team Invite'),
#         (POST_FRIEND_COMMENT, 'Post Friend Comment'),
#         (POST_FRIEND_LIKE, 'Post Friend Comment'),
#         (TEAM_MEMBER_VACANCY, 'Team Member Vacancy'),
#     )

#     user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_notifications')
#     message = models.TextField()
#     viewed = models.BooleanField(default=False)
#     created_on = models.DateTimeField(auto_now_add=True)
#     notification_type = models.IntegerField(choices=NOTIFICATION_TYPE_CHOICES)
#     click_url = models.TextField()
#     display_picture = models.ImageField(blank=True, null=True, upload_to=get_user_notification_display_picture_path)

#     def __str__(self):
#         return self.message

#     def save(cls, *args, **kwargs):
#         cls.send_email_for_notification(cls.user, cls.message, cls.notification_type, cls.click_url)
#         return super(UserNotification, cls).save(*args, **kwargs)

#     @classmethod
#     def send_email_for_notification(cls, user, message, notification_type, click_url):
#         subject = "Sportsvitae {}".format(message)
#         body = render_to_string('accounts/mailers/notification_email.html', context={'message': message, 'click_url': click_url})
#         send_mail(subject=subject, message=message, from_email='info@sportsvitae.com', recipient_list=[user.email], fail_silently=True, html_message=body)

#     @classmethod
#     def create_post_friend_liked_notification(cls, from_user, to_user, on_post, id):
#         # User Post Like Notifiaction
#         message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.POST_FRIEND_LIKE].format(friend=from_user.name)
#         # UserNotification.objects.create(user=to_user, message=message, notification_type=14, click_url='#')
#         UserNotification.objects.create(user=to_user, message=message, notification_type=14, click_url='/user/post/{}/'.format(id))

#     @classmethod
#     def create_team_post_friend_liked_notification(cls, from_user, to_user, on_post, id):
#         # Team Post Like notifications
#         message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.POST_FRIEND_LIKE].format(friend=from_user.name)
#         # UserNotification.objects.create(user=to_user, message=message, notification_type=14, click_url='#')
#         UserNotification.objects.create(user=to_user, message=message, notification_type=14, click_url='/cricket/teams/post/{}/'.format(id))

#     @classmethod
#     def create_post_friend_comment_notification(cls, from_user, to_user, on_post, id):
#         message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.POST_FRIEND_COMMENT].format(friend=from_user.name)
#         # UserNotification.objects.create(user=to_user, message=message, notification_type=13, click_url='#')
#         UserNotification.objects.create(user=to_user, message=message, notification_type=13, click_url='/user/post/{}/'.format(id))

#     @classmethod
#     def create_team_post_friend_comment_notification(cls, from_user, to_user, on_post, id):
#         message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.POST_FRIEND_COMMENT].format(friend=from_user.name)
#         # UserNotification.objects.create(user=to_user, message=message, notification_type=13, click_url='#')
#         UserNotification.objects.create(user=to_user, message=message, notification_type=13, click_url='/cricket/teams/post/{}/'.format(id))

#     @classmethod
#     def create_friend_request_accept_notification(cls, from_user, to_user):
#         message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.ACCEPT_FRIEND_REQUEST].format(friend=to_user.name)
#         click_url = reverse('user_wall', kwargs={'slug': to_user.slug})
#         display_picture = to_user.display_picture
#         UserNotification.objects.create(user=from_user, message=message, notification_type=cls.ACCEPT_FRIEND_REQUEST, click_url=click_url, display_picture=display_picture)

#     @classmethod
#     def create_new_cricket_team_notifications(cls, cricket_team, exclude_ids=[]):
#         team_members = cricket_team.get_all_team_members()
#         notification_objs = []

#         for team_member in team_members:
#             if team_member.cricketer.id not in exclude_ids:
#                 message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.ADD_CRICKET_TEAM].format(cricket_team=cricket_team.name)
#                 click_url = reverse('cricket_team_wall', kwargs={'slug': cricket_team.slug})
#                 display_picture = cricket_team.display_picture
#                 notification_obj = UserNotification(user=team_member.cricketer.user, message=message, notification_type=cls.ADD_CRICKET_TEAM, click_url=click_url, display_picture=display_picture)
#                 notification_objs.append(notification_obj)

#         # Bulk Create Objects
#         if notification_objs:
#             UserNotification.objects.bulk_create(notification_objs)

#     @classmethod
#     def create_cricket_team_captain_notification(cls, captain_user, cricket_team, exclude_ids=[]):

#         if captain_user.cricketer.id not in exclude_ids:
#             message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.ADD_CAPTAIN_CRICKET_TEAM].format(cricket_team=cricket_team)
#             click_url = reverse('cricket_team_wall', kwargs={'slug': cricket_team.slug})
#             display_picture = cricket_team.display_picture

#             UserNotification.objects.create(user=captain_user, message=message, notification_type=cls.ADD_CAPTAIN_CRICKET_TEAM, click_url=click_url, display_picture=display_picture)

#     @classmethod
#     def create_cricket_team_vice_captain_notification(cls, vice_captain_user, cricket_team, exclude_ids=[]):

#         if vice_captain_user.cricketer.id not in exclude_ids:
#             message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.ADD_VICE_CAPTAIN_CRICKET_TEAM].format(cricket_team=cricket_team)
#             click_url = reverse('cricket_team_wall', kwargs={'slug': cricket_team.slug})
#             display_picture = cricket_team.display_picture

#             UserNotification.objects.create(user=vice_captain_user, message=message, notification_type=cls.ADD_VICE_CAPTAIN_CRICKET_TEAM, click_url=click_url, display_picture=display_picture)

#     @classmethod
#     def create_new_cricket_match_notifications(cls, cricket_team, cricket_team_playing_eleven, exclude_ids=[]):
#         team_members = [x for x in cricket_team_playing_eleven if x.has_write_permissions() and x.cricketer_id not in exclude_ids]
#         notification_objs = []

#         for team_member in team_members:
#             message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.ADD_NEW_CRICKET_MATCH].format(cricket_team=cricket_team.name)
#             click_url = reverse('cricket_team_performance', kwargs={'slug': cricket_team.slug})
#             display_picture = cricket_team.display_picture
#             notification_obj = UserNotification(user=team_member.cricketer.user, message=message, notification_type=cls.ADD_NEW_CRICKET_MATCH, click_url=click_url, display_picture=display_picture)
#             notification_objs.append(notification_obj)

#         # Bulk Create Objects
#         if notification_objs:
#             UserNotification.objects.bulk_create(notification_objs)

#     @classmethod
#     def create_cricket_score_sheet_notifications(cls, cricket_team, exclude_ids=[]):
#         team_members = cricket_team.get_all_team_members()
#         notification_objs = []

#         for team_member in team_members:
#             if team_member.cricketer_id not in exclude_ids:
#                 message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.ADD_NEW_CRICKET_MATCH_SCORE_SHEET].format(cricket_team=cricket_team.name)
#                 click_url = reverse('cricket_team_performance', kwargs={'slug': cricket_team.slug})
#                 display_picture = cricket_team.display_picture
#                 notification_obj = UserNotification(user=team_member.cricketer.user, message=message, notification_type=cls.ADD_NEW_CRICKET_MATCH_SCORE_SHEET, click_url=click_url, display_picture=display_picture)
#                 notification_objs.append(notification_obj)

#         # Bulk Create Objects
#         if notification_objs:
#             UserNotification.objects.bulk_create(notification_objs)

#     @classmethod
#     def create_man_of_the_match_notification(cls, man_of_the_match_user, cricket_team, exclude_ids=[]):

#         if man_of_the_match_user.cricketer.id not in exclude_ids:
#             message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.CRICKET_MATCH_MAN_OF_THE_MATCH].format(cricket_team=cricket_team.name)
#             click_url = reverse('cricket_team_performance', kwargs={'slug': cricket_team.slug})
#             display_picture = cricket_team.display_picture

#             UserNotification.objects.create(user=man_of_the_match_user, message=message, notification_type=cls.CRICKET_MATCH_MAN_OF_THE_MATCH, click_url=click_url, display_picture=display_picture)

#     @classmethod
#     def create_best_batsman_notification(cls, best_batsman_user, cricket_team, exclude_ids=[]):

#         if best_batsman_user.cricketer.id not in exclude_ids:
#             message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.CRICKET_MATCH_BEST_BATSMAN].format(cricket_team=cricket_team.name)
#             click_url = reverse('cricket_team_performance', kwargs={'slug': cricket_team.slug})
#             display_picture = cricket_team.display_picture

#             UserNotification.objects.create(user=best_batsman_user, message=message, notification_type=cls.CRICKET_MATCH_BEST_BATSMAN, click_url=click_url, display_picture=display_picture)

#     @classmethod
#     def create_best_bowler_notification(cls, best_bowler_user, cricket_team, exclude_ids=[]):

#         if best_bowler_user.cricketer.id not in exclude_ids:
#             message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.CRICKET_MATCH_BEST_BOWLER].format(cricket_team=cricket_team)
#             click_url = reverse('cricket_team_performance', kwargs={'slug': cricket_team.slug})
#             display_picture = cricket_team.display_picture

#             UserNotification.objects.create(user=best_bowler_user, message=message, notification_type=cls.CRICKET_MATCH_BEST_BOWLER, click_url=click_url, display_picture=display_picture)

#     @classmethod
#     def create_best_fielder_notification(cls, best_fielder_user, cricket_team, exclude_ids=[]):

#         if best_fielder_user.cricketer.id not in exclude_ids:
#             message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.CRICKET_MATCH_BEST_FIELDER].format(cricket_team=cricket_team)
#             click_url = reverse('cricket_team_performance', kwargs={'slug': cricket_team.slug})
#             display_picture = cricket_team.display_picture

#             UserNotification.objects.create(user=best_fielder_user, message=message, notification_type=cls.CRICKET_MATCH_BEST_FIELDER, click_url=click_url, display_picture=display_picture)

#     @classmethod
#     def create_follow_cricket_team_notifications(cls, user, cricket_team, exclude_ids=[]):
#         team_members_with_write_permission = [x for x in cricket_team.get_all_team_members() if x.has_write_permissions() and x.cricketer_id not in exclude_ids]
#         notification_objs = []

#         for team_member in team_members_with_write_permission:
#             message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.FOLLOW_CRICKET_TEAM].format(user_name=user.name ,cricket_team=cricket_team.name)
#             click_url = reverse('user_wall', kwargs={'slug': user.slug})
#             display_picture = user.display_picture
#             notification_obj = UserNotification(user=team_member.cricketer.user, message=message, notification_type=cls.FOLLOW_CRICKET_TEAM, click_url=click_url, display_picture=display_picture)
#             notification_objs.append(notification_obj)

#         # Bulk Create Objects
#         if notification_objs:
#             UserNotification.objects.bulk_create(notification_objs)

#     @classmethod
#     def create_cricket_team_invite_notifications(cls, from_user, cricket_team, to_user):
#         message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.CRICKET_TEAM_INVITE].format(from_user=from_user.name, cricket_team=cricket_team.name)
#         click_url = reverse('cricket_team_wall', kwargs={'slug': cricket_team.slug})
#         display_picture = from_user.display_picture

#         UserNotification.objects.create(user=to_user, message=message, notification_type=cls.CRICKET_TEAM_INVITE, click_url=click_url, display_picture=display_picture)

#     @classmethod
#     def create_cricket_team_member_vacancy_notifications(cls, cricket_team, to_user):
#         message = USER_NOTIFICATION_TYPE_TO_MESSAGES_MAPPING[cls.TEAM_MEMBER_VACANCY].format(cricket_team=cricket_team.name)
#         click_url = reverse('detail_team_member_vacancy', kwargs={'slug': cricket_team.slug})
#         display_picture = cricket_team.display_picture

#         UserNotification.objects.create(user=to_user, message=message, notification_type=cls.TEAM_MEMBER_VACANCY, click_url=click_url, display_picture=display_picture)

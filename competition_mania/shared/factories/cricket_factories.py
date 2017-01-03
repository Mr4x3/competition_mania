# inbuilt python imports

# inbuilt django imports

# third-party django imports
import factory

# inter-app imports
from cricket.models import Cricketer, CricketTeam, CricketCertification, CricketTeamMember, CricketTeamWallPost, CricketTeamWallPostComment, CricketMatch, CricketMatchStat, CricketMatchBattingStat, CricketMatchBowlingStat, CricketTeamJoinRequest

# local imports
from .account_factories import UserFactory


class CricketerFactory(factory.DjangoModelFactory):

    class Meta:
        model = Cricketer

    user = factory.SubFactory(UserFactory)
    role = 'AR'
    is_wicketkeeper = True
    batsman_handling = 'R'
    batting_position = 'TO'
    bowling_arm = 'R'
    bowling_type = 'P'
    bowling_type_variation = 'F'


class BatsmanFactory(factory.DjangoModelFactory):

    class Meta:
        model = Cricketer

    user = factory.SubFactory(UserFactory)
    role = 'BM'
    batsman_handling = 'R'
    batting_position = 'TO'


class BowlerFactory(factory.DjangoModelFactory):

    class Meta:
        model = Cricketer

    user = factory.SubFactory(UserFactory)
    role = 'BL'
    bowling_arm = 'R'
    bowling_type = 'P'
    bowling_type_variation = 'F'


class CricketTeamFactory(factory.DjangoModelFactory):

    class Meta:
        model = CricketTeam

    super_admin = factory.SubFactory(CricketerFactory)
    name = 'csk'
    playing_as = 'P'
    founded_by = 'Dhoni'
    home_ground = 'Chennai'
    week_slot = 'WD'
    day_slot = 'M'
    registration_midout = False


class CricketTeamMemberFactory(factory.DjangoModelFactory):

    class Meta:
        model = CricketTeamMember

    team = factory.SubFactory(CricketTeamFactory)
    cricketer = factory.SubFactory(CricketerFactory)


class CricketCertificationFactory(factory.DjangoModelFactory):

    class Meta:
        model = CricketCertification

    cricketer = factory.SubFactory(CricketerFactory)
    title = 'ipl'
    role = 'B'


class CricketTeamWallPostFactoryMixin(factory.DjangoModelFactory):

    class Meta:
        model = CricketTeamWallPost

    posted_by = factory.LazyAttribute(lambda obj: obj.team.super_admin.user)
    team = factory.SubFactory(CricketTeamFactory)

    @factory.post_generation
    def likes(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of users were passed in, add them
            for post_liked_by in extracted:
                self.likes.add(post_liked_by)


class CricketTeamWallPostFactory(CricketTeamWallPostFactoryMixin):

    text = 'Some wall post'
    post_type = 1


class CricketTeamWallImagePostFactory(CricketTeamWallPostFactoryMixin):

    text = 'Check out this new pic'
    post_image = factory.django.ImageField(from_path='cricket/tests/test_cricket_team_wall_post_image.jpg')
    post_type = 2


class CricketTeamWallLocationPostFactory(CricketTeamWallPostFactoryMixin):

    text = 'Checked in at'
    location = 'Delhi, India'
    post_type = 3


class CricketTeamWallPostCommentFactory(factory.DjangoModelFactory):

    class Meta:
        model = CricketTeamWallPostComment
        exclude = ('cricketer',)

    cricketer = factory.SubFactory('sportsvitae.shared.factories.CricketerFactory')
    comment_by = factory.LazyAttribute(lambda obj: obj.cricketer.user)
    team_wall_post = factory.SubFactory(CricketTeamWallPostFactory)
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


class CricketMidoutMatchFactory(factory.DjangoModelFactory):

    team = factory.SubFactory(CricketTeamFactory)
    registration_midout = True

    class Meta:
        model = CricketMatch

    @factory.post_generation
    def playing_eleven(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of members were passed in, add them
            for team_member in extracted:
                self.playing_eleven.add(team_member)


class CricketMatchFactoryMixin(factory.DjangoModelFactory):

    team = factory.SubFactory(CricketTeamFactory)
    batting_innings_overs = 12
    batting_innings_wides = 3
    batting_innings_no_balls = 2
    batting_innings_byes = 4
    batting_innings_leg_byes = 5
    registration_midout = False

    class Meta:
        model = CricketMatch

    @factory.post_generation
    def playing_eleven(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of members were passed in, add them
            for team_member in extracted:
                self.playing_eleven.add(team_member)


class CricketMatchFactory(CricketMatchFactoryMixin):

    result = 'W'
    result_margin = 100
    result_margin_type = 'R'
    is_best_performance = True


class CricketMatchLostFactory(CricketMatchFactoryMixin):

    result = 'L'
    result_margin = 100
    result_margin_type = 'R'


class CricketMatchTiedFactory(CricketMatchFactoryMixin):

    result = 'T'


class CricketMatchDrawnFactory(CricketMatchFactoryMixin):

    result = 'D'


class CricketMatchNoResultFactory(CricketMatchFactoryMixin):

    result = 'N/R'


class CricketMidoutMatchStatFactory(factory.DjangoModelFactory):

    match = factory.SubFactory(CricketMidoutMatchFactory)
    against = 'KKR'

    class Meta:
        model = CricketMatchStat


class CricketMatchStatFactory(factory.DjangoModelFactory):

    match = factory.SubFactory(CricketMatchFactory)
    against = 'KKR'

    class Meta:
        model = CricketMatchStat

class CricketMatchBattingStatFactory(factory.DjangoModelFactory):

    match_stat = factory.SubFactory(CricketMatchStatFactory)
    batsman = factory.SubFactory(CricketerFactory)
    batting_position_number = 1
    dismissal_method = 'B'
    dismissal_by = 'Dinda'
    runs = 123
    balls_played = 66
    fours = 4
    sixes = 7

    class Meta:
        model = CricketMatchBattingStat


class CricketMatchBowlingStatFactory(factory.DjangoModelFactory):

    match_stat = factory.SubFactory(CricketMatchStatFactory)
    bowler = factory.SubFactory(CricketerFactory)
    overs = 12
    maiden_overs = 3
    runs = 24
    wickets = 2

    class Meta:
        model = CricketMatchBowlingStat


class CricketTeamJoinRequestFactory(factory.DjangoModelFactory):
    """
    Model for storing Cricket Team Connect Requests.
    """
    sender = factory.SubFactory(CricketerFactory)
    team = factory.SubFactory(CricketTeamFactory)

    class Meta:
        model = CricketTeamJoinRequest

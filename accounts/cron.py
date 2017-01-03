# Python Imports
import datetime

# Django Imports
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Q

# Third Party Django Imports
from django_cron import CronJobBase, Schedule

# Inter App Imports
from cricket.models import Cricketer, CricketMatchBattingStat, CricketMatchBowlingStat, CricketMatchWicketKeepingStat

# Local Imports
from .models import User


class CompleteYourProfileReminder(CronJobBase):
    # RUN_EVERY_MINS = 43200 # every 30 days
    RUN_AT_TIMES = ['17:00']
    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'accounts.CompleteYourProfileReminder'

    def do(self):
        inactivity_days = 30
        thirty_days = datetime.date.today()-datetime.timedelta(inactivity_days)
        inactive_users = User.objects.filter(last_profile_complation_mail__lte=thirty_days, registration_midout=True)
        subject = '[Important] Inactivity Notice'
        body = render_to_string('accounts/mailers/profile_not_completed.html', context={})
        for user in inactive_users:
            recipient = [user.email]

            send_mail(subject=subject, message='', from_email='info@sportsvitae.com', recipient_list=recipient, fail_silently=True, html_message=body)

        inactive_users.update(last_profile_complation_mail=timezone.now())


class AddMatchStatsReminder(CronJobBase):
    # RUN_EVERY_MINS = 14400 # every 10 days
    RUN_AT_TIMES = ['17:30']
    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'accounts.AddMatchStatsReminder'

    def do(self):
        inactivity_days = 10
        ten_days = datetime.date.today() - datetime.timedelta(inactivity_days)

        batsmen = CricketMatchBattingStat.objects.filter(match_stat__match_date__gte=ten_days, match_stat__match=None).values_list('batsman', flat=True)
        bowlers = CricketMatchBowlingStat.objects.filter(match_stat__match_date__gte=ten_days, match_stat__match=None).values_list('bowler', flat=True)
        wicketkeepers = CricketMatchWicketKeepingStat.objects.filter(match_stat__match_date__gte=ten_days, match_stat__match=None).values_list('wicketkeeper', flat=True)

        cricketer_ids = list(batsmen) + list(bowlers) + list(wicketkeepers)
        cricketer_ids = set(cricketer_ids)

        cricketers = Cricketer.objects.exclude(id__in=cricketer_ids).filter(last_inactivity_mail__lte=ten_days)

        # recipient_list = []
        subject = '[Important] Inactivity Notice'
        body = render_to_string('accounts/mailers/inactivity_mail.html', context={})
        for cricketer in cricketers:
            recipient = [cricketer.user.email]

            send_mail(subject=subject, message='', from_email='info@sportsvitae.com', recipient_list=recipient, fail_silently=True, html_message=body)

        cricketers.update(last_inactivity_mail=timezone.now())

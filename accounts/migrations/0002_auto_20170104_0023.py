# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-01-03 18:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='slug',
            field=models.SlugField(blank=True, max_length=70),
        ),
    ]

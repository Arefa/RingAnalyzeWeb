# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-10 14:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyze', '0005_auto_20160510_2037'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConvergeNE',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cne_name', models.CharField(max_length=100)),
                ('cne_type', models.CharField(max_length=100)),
                ('ring_name', models.CharField(max_length=100)),
                ('ring_region', models.CharField(max_length=10)),
            ],
        ),
    ]

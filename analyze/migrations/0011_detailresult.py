# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-06 12:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('analyze', '0010_errormsg_ring_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='DetailResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ring_name', models.CharField(max_length=100)),
                ('ne_num', models.CharField(max_length=100)),
                ('bar_ne', models.TextField(max_length=1000)),
                ('cne_point', models.CharField(max_length=100)),
                ('bcne_cne', models.CharField(max_length=100)),
                ('lsc_num', models.CharField(max_length=100)),
                ('lsc_ne', models.TextField(max_length=1000)),
                ('arr', models.CharField(max_length=100)),
                ('arr_ne', models.TextField(max_length=1000)),
                ('dr', models.CharField(max_length=100)),
                ('arp', models.TextField(max_length=1000)),
                ('msg', models.CharField(max_length=500)),
            ],
        ),
    ]

# Generated by Django 2.2.4 on 2020-12-11 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_bigbluebutton', '0012_meetinglog_meeting'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meetinglog',
            name='meeting',
        ),
        migrations.AddField(
            model_name='meetinglog',
            name='meeting_id',
            field=models.CharField(default='', max_length=100, verbose_name='Meeting ID'),
        ),
    ]

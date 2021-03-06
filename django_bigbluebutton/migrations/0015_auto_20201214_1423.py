# Generated by Django 2.2.5 on 2020-12-14 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_bigbluebutton', '0014_auto_20201211_0920'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meeting',
            name='logout_url',
            field=models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='URL to visit after user logged out'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='meeting_id',
            field=models.CharField(max_length=200, unique=True, verbose_name='Meeting ID'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Name of Meeting'),
        ),
    ]

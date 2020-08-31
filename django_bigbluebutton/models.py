import django_jalali.db.models as jmodels
from django.db import models

from .bbb import BigBlueButton


class Meeting(models.Model):
    """
        This models hold information about each meeting room.
        When creating a big blue button room with BBB APIs,
        Will store it's info here for later usages.
    """
    name = models.CharField(max_length=100)
    meeting_id = models.CharField(max_length=100, unique=True)
    attendee_password = models.CharField(max_length=50)
    moderator_password = models.CharField(max_length=50)

    created_at = jmodels.jDateTimeField(auto_now_add=True)
    updated_at = jmodels.jDateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}'.format(self.id, self.name)

    @property
    def is_running(self):
        return BigBlueButton().is_running(self.meeting_id)

    def start(self):
        return BigBlueButton().start(
            name=self.name,
            meeting_id=self.meeting_id,
            attendee_password=self.attendee_password,
            moderator_password=self.moderator_password
        )

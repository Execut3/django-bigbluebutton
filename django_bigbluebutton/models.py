import django_jalali.db.models as jmodels
from django.db import models

from .bbb import BigBlueButton
from .utils import xml_to_json


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
    parent_meeting_id = models.CharField(null=True, blank=True, max_length=100)
    internal_meeting_id = models.CharField(null=True, blank=True, max_length=100)
    welcome_text = models.TextField(default='Welcome!')
    voice_bridge = models.CharField(max_length=50, null=True, blank=True)

    is_running = models.BooleanField(
        default=False,
        help_text='Indicates whether this meeting is running in BigBlueButton or not!'
    )

    # Time related Info
    created_at = jmodels.jDateTimeField(auto_now_add=True)
    updated_at = jmodels.jDateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}'.format(self.id, self.name)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.name:
            self.name = self.meeting_id
        super(Meeting, self).save()

    def check_is_running(self, commit=True):
        self.is_running = BigBlueButton().is_running(self.meeting_id)
        if commit:
            self.save()
        return self.is_running

    def start(self):
        """ Will start already created meeting again. """
        return BigBlueButton().start(
            name=self.name,
            meeting_id=self.meeting_id,
            attendee_password=self.attendee_password,
            moderator_password=self.moderator_password
        )

    def end(self):
        ended = BigBlueButton().end_meeting(self.meeting_id, self.moderator_password)
        return ended    # If successfully ended, will return True

    def create_join_link(self, fullname, role='moderator'):
        meeting = Meeting.create(self.name, self.meeting_id, self.welcome_text)
        pw = meeting.moderator_password if role == 'moderator' else meeting.attendee_password
        return BigBlueButton().join_url(meeting.meeting_id, fullname, pw)

    @classmethod
    def create(cls, name, meeting_id, meeting_welcome='Welcome!'):
        m_xml = BigBlueButton().start(
            name=name,
            meeting_id=meeting_id,
            welcome=meeting_welcome
        )
        print(m_xml)
        meeting_json = xml_to_json(m_xml)
        if meeting_json['returncode'] != 'SUCCESS':
            raise ValueError('Unable to create meeting!')

        # Now create a model for it.
        meeting, _ = Meeting.objects.get_or_create(meeting_id=meeting_id)
        meeting.name = name
        meeting.welcome_text = meeting_json['meetingID']
        meeting.attendee_password = meeting_json['attendeePW']
        meeting.moderator_password = meeting_json['moderatorPW']
        meeting.internal_meeting_id = meeting_json['internalMeetingID']
        meeting.parent_meeting_id = meeting_json['parentMeetingID']
        meeting.voice_bridge = meeting_json['voiceBridge']
        meeting.save()

        return meeting

    @classmethod
    def update_running_meetings(cls):
        """ This method will call bigbluebutton,
        fetch running meetings on bbb, and update local
        database with running meetings info. """
        running_meetings = BigBlueButton().get_meetings()
        print(running_meetings)

        """ A sample response from bigbluebutton.getMeeting():
        [
            {
                'name': 'meeting-10', 'running': 'true', 
                'moderator_pw': 'mp', 'attendee_pw': 'ap', 
                'info': {
                    'start_time': '1599199672948', 'end_time': '0', 
                    'participant_count': '1', 'moderator_count': '1',
                     'moderator_pw': 'mp', 'attendee_pw': 'ap'
                }
            }
        ]
        """

        meetings_id_list = [item['name'] for item in running_meetings]
        Meeting.objects.all().update(is_running=False)
        Meeting.objects.filter(meeting_id__in=meetings_id_list).update(is_running=True)

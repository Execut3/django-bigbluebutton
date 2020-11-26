import logging

from django.db import models
from django.utils.translation import ugettext_lazy as _

from .settings import *
from .bbb import BigBlueButton
from .utils import xml_to_json


class Meeting(models.Model):
    """ This models hold information about each meeting room.
        When creating a big blue button room with BBB APIs,
        Will store it's info here for later usages.
    """
    name = models.CharField(
        max_length=100,
        verbose_name=_('Name of Meeting')
    )
    meeting_id = models.CharField(
        max_length=100, unique=True,
        verbose_name=_('Meeting ID')
    )
    attendee_password = models.CharField(
        max_length=50,
        verbose_name=_('Attendee Password')
    )
    moderator_password = models.CharField(
        max_length=50,
        verbose_name=_('Moderator Password')
    )
    is_running = models.BooleanField(
        default=False,
        verbose_name=_('Is running'),
        help_text=_('Indicates whether this meeting is running in BigBlueButton or not!')
    )

    # Configs
    max_participants = models.IntegerField(
        default=10,
        verbose_name=_('Max Participants')
    )
    welcome_text = models.TextField(
        default=_('Welcome!'),
        verbose_name=_('Meeting Text in Bigbluebutton')
    )
    logout_url = models.CharField(
        max_length=200,
        default='', null=True, blank=True,
        verbose_name=_('URL to visit after user logged out')
    )
    record = models.BooleanField(
        default=True,
        verbose_name=_('Record')
    )
    auto_start_recording = models.BooleanField(
        default=False,
        verbose_name=_('Auto Start Recording')
    )
    allow_start_stop_recording = models.BooleanField(
        default=True,
        verbose_name=_('Allow Stop/Start Recording'),
        help_text=_('Allow the user to start/stop recording. (default true)')
    )
    webcam_only_for_moderators = models.BooleanField(
        default=False,
        verbose_name=_('Webcam Only for moderators?'),
        help_text=_('will cause all webcams shared by viewers '
                    'during this meeting to only appear for moderators')
    )

    # Lock settings
    lock_settings_disable_cam = models.BooleanField(
        default=False,
        verbose_name=_('Disable Camera'),
        help_text=_('will prevent users from sharing their camera in the meeting')
    )
    lock_settings_disable_mic = models.BooleanField(
        default=False,
        verbose_name=_('Disable Mic'),
        help_text=_('will only allow user to join listen only')
    )
    lock_settings_disable_private_chat = models.BooleanField(
        default=False,
        verbose_name=_('Disable Private chat'),
        help_text=_('if True will disable private chats in the meeting')
    )
    lock_settings_disable_public_chat = models.BooleanField(
        default=False,
        verbose_name=_('Disable public chat'),
        help_text=_('if True will disable public chat in the meeting')
    )
    lock_settings_disable_note = models.BooleanField(
        default=False,
        verbose_name=_('Disable Note'),
        help_text=_('if True will disable notes in the meeting.')
    )
    lock_settings_locked_layout = models.BooleanField(
        default=False,
        verbose_name=_('Locked Layout'),
        help_text=_('will lock the layout in the meeting. ')
    )

    # Not important Info
    parent_meeting_id = models.CharField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Parent Meeting ID')
    )
    internal_meeting_id = models.CharField(
        null=True,
        blank=True,
        max_length=100,
        verbose_name=_('Internal Meeting ID')
    )
    voice_bridge = models.CharField(
        max_length=50,
        null=True, blank=True,
        verbose_name=_('Voice Bridge')
    )

    # Time related Info
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}'.format(self.id, self.name)

    class Meta:
        db_table = 'meeting'
        verbose_name = 'Meeting'
        verbose_name_plural = _('Meeting')

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.name:
            self.name = self.meeting_id
        super(Meeting, self).save()

    @property
    def info(self):
        # Will return result of bbb.get_meeting_info
        return BigBlueButton().meeting_info(
            self.meeting_id,
            self.moderator_password
        )

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
        # If successfully ended, will return True
        ended = BigBlueButton().end_meeting(
            meeting_id=self.meeting_id,
            password=self.moderator_password
        )
        ended = True if ended == True else False
        if ended:
            self.is_running = False
            self.save()

            # Now send a signal so other apps also be notified
            from .signals import meeting_ended
            meeting_ended.send(sender=self)
        return ended

    def create_join_link(self, fullname, role='moderator', **kwargs):
        pw = self.moderator_password if role == 'moderator' else self.attendee_password
        link = BigBlueButton().join_url(self.meeting_id, fullname, pw, **kwargs)
        return link

    @classmethod
    def create(cls, name, meeting_id, **kwargs):

        kwargs.update({
            'record': kwargs.get('record', BBB_RECORD),
            'logout_url': kwargs.get('logout_url', BBB_LOGOUT_URL),
            'auto_start_recording': kwargs.get('auto_start_recording', BBB_AUTO_RECORDING),
            'allow_start_stop_recording': kwargs.get('allow_start_stop_recording', BBB_ALLOW_START_STOP_RECORDING),
        })

        m_xml = BigBlueButton().start(name=name, meeting_id=meeting_id, **kwargs)
        print(m_xml)
        meeting_json = xml_to_json(m_xml)
        if meeting_json['returncode'] != 'SUCCESS':
            raise ValueError('Unable to create meeting!')

        # Now create a model for it.
        meeting, _ = Meeting.objects.get_or_create(meeting_id=meeting_id)

        meeting.name = name
        meeting.is_running = True
        meeting.record = kwargs.get('record', True)
        meeting.welcome_text = meeting_json['meetingID']
        meeting.logout_url = kwargs.get('logout_url', '')
        meeting.voice_bridge = meeting_json['voiceBridge']
        meeting.attendee_password = meeting_json['attendeePW']
        meeting.moderator_password = meeting_json['moderatorPW']
        meeting.parent_meeting_id = meeting_json['parentMeetingID']
        meeting.internal_meeting_id = meeting_json['internalMeetingID']
        meeting.auto_start_recording = kwargs.get('auto_start_recording', True)
        meeting.allow_start_stop_recording = kwargs.get('allow_start_stop_recording', True)
        meeting.save()

        return meeting

    @classmethod
    def update_running_meetings(cls):
        """ This method will call bigbluebutton,
        fetch running meetings on bbb, and update local
        database with running meetings info. """
        running_meetings = BigBlueButton().get_meetings()

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

        try:
            # First get list of running meetings from bbb
            meetings_id_list = [item['meeting_id'] for item in running_meetings]

            # Now update all to not running
            Meeting.objects.all().update(is_running=False)

            # Find meetings with proper id_list running, and update their model status to running
            Meeting.objects.filter(meeting_id__in=meetings_id_list).update(is_running=True)
        except Exception as e:
            logging.error('[-] Exception in update_running_meetings, {}'.format(str(e)))

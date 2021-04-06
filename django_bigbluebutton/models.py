import logging
import datetime

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _

from .settings import *
from .bbb import BigBlueButton
from .utils import xml_to_json

User = get_user_model()


class Meeting(models.Model):
    """ This models hold information about each meeting room.
        When creating a big blue button room with BBB APIs,
        Will store it's info here for later usages.
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_('Meeting Name')
    )
    meeting_id = models.CharField(
        max_length=200, unique=True,
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
        max_length=500,
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

    # Hook related info
    hook_id = models.CharField(
        null=True, blank=True,
        max_length=50, default='',
        verbose_name=_('Hook ID received from BBB')
    )
    hook_url = models.CharField(
        default='',
        max_length=500,
        null=True, blank=True,
        verbose_name=_('Hook URL')
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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
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
        """ Call bbb is_running method, and see if this meeting_id is running! """
        is_running = BigBlueButton().is_running(self.meeting_id)
        self.is_running = True if is_running in ['true', True, 'True'] else False
        if commit:
            self.save()
        return self.is_running

    def start(self):
        """ Will start already created meeting again. """
        result = BigBlueButton().start(
            name=self.name,
            meeting_id=self.meeting_id,
            attendee_password=self.attendee_password,
            moderator_password=self.moderator_password
        )

        if result:
            # It's better to create hook again,
            # So if by any reason is removed from bbb, again be created
            # If already exist will just give warning and will be ignored
            self.create_hook()

        return result

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

    def create_hook(self):
        """ By calling this method, will create a hook to callback-url for this meeting-id

        TODO: Maybe it's better to delete hooks first then create new one.
        """
        callback_url = settings.BBB_CALLBACK_URL
        if callback_url:
            try:
                # Be noted meeting_id is different from id,
                # meeting_id is like meeting-11 (value to know in bbb)
                # id is just primary key for Meeting instance
                if not self.hook_url:
                    self.hook_url = '{callback}/api/meeting/{id}/callback/'.format(
                        id=self.id,
                        callback=str(callback_url).rstrip('/'),
                    )
                output = BigBlueButton().create_hook(self.hook_url, self.meeting_id)
                if output.get('hook_id'):
                    self.hook_id = output['hook_id']
                    self.save()
            except Exception as e:
                error_msg = 'Error in setting api hook for meeting: {}, {}'.format(self.meeting_id, str(e))
                logging.error(error_msg)

    def delete_hook(self):
        if self.hook_id:
            BigBlueButton().destroy_hook(self.hook_id)

    def get_report(self):
        """ This method will return useful info about participants in meeting.

        return will be like this:

            {
                "activity_logs": [
                    {
                        'user': {
                            'id': '432',
                            'fullname': 'Execut3'
                        },
                        'join_date': '2020-10-20',
                        'left_date': None
                    }
                ],
                "presence_time_logs": {
                    '432': {
                        'duration': 123,
                        'fullname': 'Execut3'
                    }
                }
            }
        """
        logs = MeetingLog.objects. \
            filter(meeting__meeting_id=self.meeting_id). \
            select_related('user'). \
            order_by('-updated_at')
        logs = list(logs)   # Convert to list

        # A dict which it's keys are user_id s (overall seconds each user was in meeting)
        presence_time_logs = {}

        # A list of logs of users in the meeting. for example when they joined, when left and ...
        activity_logs = []

        # Now iterate on logs and calc duration and fill update variables.
        for log in logs:
            try:
                userkey = log.fullname
                if log.user:
                    userkey = log.user.id
                userkey = str(userkey)

                # Now will try to find diff of left_date and join date
                # To calc duration of log. If already not left, will check
                # current date for left date. If error will be 0
                try:
                    if log.left_date:
                        duration = (log.left_date - log.join_date).seconds
                    else:
                        now = datetime.datetime.now()
                        duration = (now - log.join_date).seconds
                except:
                    duration = 0

                if userkey in presence_time_logs.keys():
                    try:
                        c = presence_time_logs[userkey]['duration']
                    except Exception as e:
                        print(e)
                        c = 0
                    try:
                        presence_time_logs[userkey]['duration'] = c + duration
                    except:
                        presence_time_logs[userkey] = {
                            'duration': duration,
                            'fullname': log.fullname
                        }
                else:
                    presence_time_logs[userkey] = {
                        'duration': duration,
                        'fullname': log.fullname
                    }

                tmp = {
                    'user': {
                        'id': userkey,
                        'fullname': log.fullname
                    },
                    'join_date': log.join_date,
                    'left_date': log.left_date
                }
                activity_logs.append(tmp)
            except Exception as e:
                logging.error(str(e))

        return {
            'activity_logs': activity_logs,
            'presence_time_logs': presence_time_logs,
        }

    @classmethod
    def create(cls, name, meeting_id, **kwargs):
        kwargs.update({
            'record': kwargs.get('record', BBB_RECORD),
            'logout_url': kwargs.get('logout_url', BBB_LOGOUT_URL),
            'welcome_text': kwargs.get('welcome_text', BBB_WELCOME_TEXT),
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
        meeting.logout_url = kwargs.get('logout_url', '')
        meeting.voice_bridge = meeting_json['voiceBridge']
        meeting.attendee_password = meeting_json['attendeePW']
        meeting.moderator_password = meeting_json['moderatorPW']
        meeting.parent_meeting_id = meeting_json['parentMeetingID']
        meeting.internal_meeting_id = meeting_json['internalMeetingID']
        meeting.welcome_text = kwargs.get('welcome_text', BBB_WELCOME_TEXT)
        meeting.auto_start_recording = kwargs.get('auto_start_recording', True)
        meeting.allow_start_stop_recording = kwargs.get('allow_start_stop_recording', True)
        meeting.save()

        # Register a hook for this meeting
        meeting.create_hook()

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


class MeetingRecord(models.Model):
    """ Will hold recorded sessions of each meeting in this model.
    """
    meeting = models.ForeignKey(
        null=True,
        blank=True,
        to=Meeting,
        db_index=True,
        related_name='records',
        verbose_name=_('Meeting'),
        on_delete=models.SET_NULL,
    )
    name = models.CharField(
        default='',
        max_length=255,
        verbose_name=_('Record name')
    )
    record_id = models.CharField(
        null=True,
        blank=True,
        db_index=True,
        max_length=255,
        verbose_name=_('Record ID'),
    )
    link = models.CharField(
        null=True,
        blank=True,
        max_length=500,
        verbose_name=_('Link'),
    )

    def __str__(self):
        return '{}, {}'.format(self.meeting.name, self.record_id)

    class Meta:
        db_table = 'meeting_record'
        verbose_name = 'Meeting Record'
        verbose_name_plural = _("Meeting Record")


class MeetingLog(models.Model):
    """ Will store detail logs about user joins and disconnects.

    By joining each user, a new record will be created,
    and when user left the meeting or the meeting ended,
    It will close that log and set the end_date for it.
    """
    user = models.ForeignKey(
        to=User,
        null=True,
        blank=True,
        db_index=True,
        verbose_name=_('User'),
        on_delete=models.SET_NULL,
        related_name='meeting_log',
    )  # It can be null
    fullname = models.CharField(
        null=True,
        blank=True,
        default='',
        max_length=50,
        verbose_name=_('User fullname')
    )
    meeting = models.ForeignKey(
        null=True,
        blank=True,
        to=Meeting,
        related_name='logs',
        verbose_name=_('Meeting'),
        on_delete=models.SET_NULL,
    )
    join_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Join Date')
    )
    left_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Left Date')
    )

    # Time related Info
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}-{}'.format(self.id, self.fullname)

    class Meta:
        db_table = 'meeting_log'
        verbose_name = 'Meeting Log'
        verbose_name_plural = _('Meeting Log')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        # If already created, should update all prev logs for this meeting and set their left_date
        if not self.pk:
            now_date = datetime.datetime.now()
            MeetingLog.objects.filter(
                user=self.user,
                meeting_id=self.meeting_id,
                left_date__isnull=True
            ).update(left_date=now_date)

        if self.user:
            self.fullname = self.user.fullname

        super(MeetingLog, self).save()

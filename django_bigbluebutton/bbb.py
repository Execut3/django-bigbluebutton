import urllib
import random
import requests

from hashlib import sha1

from . import settings
from .utils import parse_xml


class BigBlueButton:
    secret_key = settings.BBB_SECRET_KEY
    api_url = settings.BBB_API_URL
    attendee_password = 'ap'
    moderator_password = 'mp'

    def api_call(self, query, call):
        prepared = '{}{}{}'.format(call, query, self.secret_key)
        checksum = sha1(str(prepared).encode('utf-8')).hexdigest()
        result = "%s&checksum=%s" % (query, checksum)
        return result

    def is_running(self, meeting_id):
        call = 'isMeetingRunning'
        query = urllib.parse.urlencode((
            ('meetingID', meeting_id),
        ))
        hashed = self.api_call(query, call)
        url = self.api_url + call + '?' + hashed
        result = parse_xml(requests.get(url).content)
        if result:
            return result.find('running').text
        else:
            return 'error'

    def end_meeting(self, meeting_id, password):
        print(password)
        call = 'end'
        query = urllib.parse.urlencode((
            ('meetingID', meeting_id),
            ('password', password),
        ))
        hashed = self.api_call(query, call)
        url = self.api_url + call + '?' + hashed
        req = requests.get(url)
        print(req.content)
        result = parse_xml(req.content)
        if result:
            return True
        else:
            return False

    def meeting_info(self, meeting_id, password):
        call = 'getMeetingInfo'
        query = urllib.parse.urlencode((
            ('meetingID', meeting_id),
            ('password', password),
        ))
        hashed = self.api_call(query, call)
        url = self.api_url + call + '?' + hashed
        r = parse_xml(requests.get(url).content)
        if r:
            # Create dict of values for easy use in template
            d = {
                'start_time': r.find('startTime').text,
                'end_time': r.find('endTime').text,
                'participant_count': r.find('participantCount').text,
                'moderator_count': r.find('moderatorCount').text,
                'moderator_pw': r.find('moderatorPW').text,
                'attendee_pw': r.find('attendeePW').text,
                # 'invite_url': reverse('join', args=[meeting_id]),
            }
            return d
        else:
            return None

    def get_meetings(self):
        call = 'getMeetings'
        query = urllib.parse.urlencode((
            ('random', 'random'),
        ))
        hashed = self.api_call(query, call)
        url = self.api_url + call + '?' + hashed
        result = parse_xml(requests.get(url).content)
        if result:
            # Create dict of values for easy use in template
            d = []
            r = result[1].findall('meeting')
            for m in r:
                meeting_id = m.find('meetingID').text
                password = m.find('moderatorPW').text
                d.append({
                    'name': meeting_id,
                    'running': m.find('running').text,
                    'moderator_pw': password,
                    'attendee_pw': m.find('attendeePW').text,
                    'info': self.meeting_info(
                        meeting_id,
                        password)
                })
            return d
        else:
            return 'error'

    def join_url(self, meeting_id, name, password):
        call = 'join'
        query = urllib.parse.urlencode((
            ('fullName', name),
            ('meetingID', meeting_id),
            ('password', password),
        ))
        hashed = self.api_call(query, call)
        url = self.api_url + call + '?' + hashed
        return url

    def start(self, name, meeting_id, **kwargs):
        call = 'create'
        attendee_password = kwargs.get("attendee_password", self.attendee_password)
        moderator_password = kwargs.get("moderator_password", self.moderator_password)

        # Get extra configs or set default values
        welcome = kwargs.get('meeting_welcome', 'Welcome!')
        record = kwargs.get('record', settings.BBB_RECORD)
        auto_start_recording = kwargs.get('auto_start_recording', settings.BBB_AUTO_RECORDING)
        allow_start_stop_recording = kwargs.get('allow_start_stop_recording', settings.BBB_ALLOW_START_STOP_RECORDING)
        logout_url = kwargs.get('logout_url', settings.BBB_LOGOUT_URL)
        webcam_only_for_moderators = kwargs.get('webcam_only_for_moderators', settings.BBB_WEBCAM_ONLY_FOR_MODS)
        voice_bridge = 70000 + random.randint(0, 9999)

        # Making the query string
        query = urllib.parse.urlencode((
            ('name', name),
            ('meetingID', meeting_id),
            ('attendeePW', attendee_password),
            ('moderatorPW', moderator_password),
            ('record', record),
            ('welcome', welcome),
            ('logoutUrl', logout_url),
            ('voiceBridge', voice_bridge),
            ('autoStartRecording', auto_start_recording),
            ('allowStartStopRecording', allow_start_stop_recording),
            ('webcamsOnlyForModerator', webcam_only_for_moderators),
        ))
        hashed = self.api_call(query, call)
        url = self.api_url + call + '?' + hashed
        result = parse_xml(requests.get(url).content.decode('utf-8'))
        if result:
            return result
        else:
            raise

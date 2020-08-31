import urllib
import random
import requests

from hashlib import sha1
from django.conf import settings

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
        call = 'end'
        query = urllib.parse.urlencode((
            ('meetingID', meeting_id),
            ('password', password),
        ))
        hashed = self.api_call(query, call)
        url = self.api_url + call + '?' + hashed
        print(requests.get(url).content)
        result = parse_xml(requests.get(url).content)
        if result:
            pass
        else:
            return 'error'

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

    def start(self, name, meeting_id, attendee_password='', moderator_password='', welcome='Welcome!'):
        call = 'create'
        if not attendee_password:
            attendee_password = self.attendee_password
        if not moderator_password:
            moderator_password = self.moderator_password
        voicebridge = 70000 + random.randint(0, 9999)
        query = urllib.parse.urlencode((
            ('name', name),
            ('meetingID', meeting_id),
            ('attendeePW', attendee_password),
            ('moderatorPW', moderator_password),
            ('voiceBridge', voicebridge),
            ('welcome', welcome),
            ('webcamsOnlyForModerator', 'true')
        ))
        hashed = self.api_call(query, call)
        url = self.api_url + call + '?' + hashed
        result = parse_xml(requests.get(url).content.decode('utf-8'))
        if result:
            return result
        else:
            raise

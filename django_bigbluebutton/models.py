import urllib
import random
import requests

from hashlib import sha1
from django.db import models
from django.conf import settings

import django_jalali.db.models as jmodels
import xml.etree.ElementTree as ET


def parse(response):
    try:
        xml = ET.XML(response)
        code = xml.find('returncode').text
        if code == 'SUCCESS':
            return xml
        else:
            raise
    except:
        return None


class Meeting(models.Model):
    """ This models hold information about each meeting room.
    When creating a big blue button room with BBB APIs, will store
    it's info here for later usages.
    """
    name = models.CharField(max_length=100)
    meeting_id = models.CharField(max_length=100, unique=True)
    attendee_password = models.CharField(max_length=50)
    moderator_password = models.CharField(max_length=50)

    created_at = jmodels.jDateTimeField(auto_now_add=True)
    updated_at = jmodels.jDateTimeField(auto_now=True)

    @classmethod
    def api_call(cls, query, call):
        prepared = '{}{}{}'.format(call, query, settings.BBB_SECRET_KEY)
        checksum = sha1(str(prepared).encode('utf-8')).hexdigest()
        result = "%s&checksum=%s" % (query, checksum)
        return result

    def is_running(self):
        call = 'isMeetingRunning'
        query = urllib.parse.urlencode((
            ('meetingID', self.meeting_id),
        ))
        hashed = self.api_call(query, call)
        url = settings.BBB_API_URL + call + '?' + hashed
        result = parse(requests.get(url).content)
        if result:
            return result.find('running').text
        else:
            return 'error'

    @classmethod
    def end_meeting(cls, meeting_id, password):
        call = 'end'
        query = urllib.parse.urlencode((
            ('meetingID', meeting_id),
            ('password', password),
        ))
        hashed = cls.api_call(query, call)
        url = settings.BBB_API_URL + call + '?' + hashed
        result = parse(requests.get(url).content)
        if result:
            pass
        else:
            return 'error'

    @classmethod
    def meeting_info(cls, meeting_id, password):
        call = 'getMeetingInfo'
        query = urllib.parse.urlencode((
            ('meetingID', meeting_id),
            ('password', password),
        ))
        hashed = cls.api_call(query, call)
        url = settings.BBB_API_URL + call + '?' + hashed
        r = parse(requests.get(url).content)
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

    @classmethod
    def get_meetings(cls):
        call = 'getMeetingss'
        query = urllib.parse.urlencode((
            ('random', 'random'),
        ))
        hashed = cls.api_call(query, call)
        url = settings.BBB_API_URL + call + '?' + hashed
        result = parse(requests.get(url).content)
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
                    'info': Meeting.meeting_info(
                        meeting_id,
                        password)
                })
            return d
        else:
            return 'error'

    def start(self):
        call = 'create'
        voicebridge = 70000 + random.randint(0, 9999)
        query = urllib.parse.urlencode((
            ('name', self.name),
            ('meetingID', self.meeting_id),
            ('attendeePW', self.attendee_password),
            ('moderatorPW', self.moderator_password),
            ('voiceBridge', voicebridge),
            ('welcome', "Welcome!"),
        ))
        hashed = self.api_call(query, call)
        url = settings.BBB_API_URL + call + '?' + hashed
        result = parse(requests.get(url).content)
        if result:
            return result
        else:
            raise

    @classmethod
    def join_url(cls, meeting_id, name, password):
        call = 'join'
        query = urllib.parse.urlencode((
            ('fullName', name),
            ('meetingID', meeting_id),
            ('password', password),
        ))
        hashed = cls.api_call(query, call)
        url = settings.BBB_API_URL + call + '?' + hashed
        return url

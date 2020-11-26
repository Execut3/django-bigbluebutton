from django.test import TestCase

from .models import Meeting
from .bbb import BigBlueButton
from .utils import xml_to_json


class BBBTest(TestCase):

    def test_get_meetings(self):
        """ Test if BigBlueButton's get_meeting method is working or not.
        It should return list of all running meetings right now!. """
        meetings = BigBlueButton().get_meetings()
        print(meetings)

        # If error in getMeetings() will return 'error' value instead of list of meeting rooms
        self.assertTrue(meetings != 'error')

        self.assertTrue(type(meetings) == list)

    def test_create_meeting(self):
        """ Will try to create a meeting with bbb.

        Example output as json from bbb 'create' command:

        {'returncode': 'SUCCESS', 'meetingID': 'test',
        'internalMeetingID': 'a94a8fe5ccb19ba61c4c0873d391e987982fbbd3-1598891360456',
        'parentMeetingID': 'bbb-none', 'attendeePW': 'ap', 'moderatorPW': 'mp',
        'createTime': '1598891360456', 'voiceBridge': '73362', 'dialNumber': '613-555-1234',
        'createDate': 'Mon Aug 31 12:29:20 EDT 2020', 'hasUserJoined': 'false',
        'duration': '0', 'hasBeenForciblyEnded': 'false', 'messageKey': None, 'message': None}
        """
        meeting_name = 'test'
        meeting_id = 'test'
        meeting_welcome = 'test meeting welcome!'

        # First step is to request BBB and create a meeting
        m_xml = BigBlueButton().start(
            name=meeting_name,
            meeting_id=meeting_id,
            welcome=meeting_welcome
        )
        meeting_json = xml_to_json(m_xml)
        self.assertTrue(meeting_json['returncode'] == 'SUCCESS')
        self.assertTrue(meeting_json['meetingID'] == meeting_id)

        # Now create a model for it.
        current_meetings = Meeting.objects.count()
        meeting, _ = Meeting.objects.get_or_create(meeting_id=meeting_json['meetingID'])
        meeting.meeting_id = meeting_json['meetingID']
        meeting.name = meeting_name
        meeting.welcome_text = meeting_json['meetingID']
        meeting.attendee_password = meeting_json['attendeePW']
        meeting.moderator_password = meeting_json['moderatorPW']
        meeting.internal_meeting_id = meeting_json['internalMeetingID']
        meeting.parent_meeting_id = meeting_json['parentMeetingID']
        meeting.voice_bridge = meeting_json['voiceBridge']
        meeting.save()

        self.assertFalse(Meeting.objects.count() == current_meetings)

    def test_create_meeting2(self):
        """ Will just call cls method in Meeting model. """
        meeting_name = 'test2'
        meeting_id = 'test2'
        meeting_welcome = 'test meeting welcome!'
        m = Meeting.create(meeting_name, meeting_id, meeting_welcome=meeting_welcome)
        self.assertTrue(type(m) == Meeting)

    def test_create_and_join_meeting(self):
        """ Will just call cls method in Meeting model. """
        meeting_name = 'test'
        meeting_id = 'testtttt'
        meeting_welcome = 'test meeting welcome!'
        meeting = Meeting.create(meeting_name, meeting_id, meeting_welcome=meeting_welcome)

        b = BigBlueButton().join_url(meeting.meeting_id, 'Moderator of Class', meeting.moderator_password)
        print('As moderator: {}'.format(b))
        # It will print a link. join with it and see if it's ok or not!

        b = BigBlueButton().join_url(meeting.meeting_id, 'reza torkaman ahmadi', meeting.attendee_password)
        print('As attendee: {}'.format(b))

    def test_join_existing_meeting(self):
        meeting_id = 'ranxbqe6jfh1g53ymcnfr2p8elhcduoxsklwb2kr'
        b = BigBlueButton().join_url(meeting_id, 'Test User', 'dYHwpBBjlZoI')
        print(b)

    def test_end_meeting(self):
        meeting_name = 'test'
        meeting_id = 'test'
        meeting_welcome = 'test meeting welcome!'
        meeting = Meeting.create(meeting_name, meeting_id, meeting_welcome=meeting_welcome)

        status = BigBlueButton().end_meeting('test', meeting.moderator_password)
        print(status)

    def test_get_meeting_info_method(self):
        """ In this test, Will test if get_meeting_info method
        is working or not, and does it have usefull info like
        list of """

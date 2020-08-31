from django.test import TestCase

from .models import Meeting


class BBBTest(TestCase):

    def test_get_meetings(self):
        meetings = Meeting.get_meetings()

        # If error in getMeetings() will return 'error' value instead of list of meeting rooms
        self.assertTrue(meetings != 'error')

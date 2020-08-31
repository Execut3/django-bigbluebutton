from django.test import TestCase

from .models import Meeting
from .bbb import BigBlueButton


class BBBTest(TestCase):

    def test_get_meetings(self):
        meetings = BigBlueButton().get_meetings()

        # If error in getMeetings() will return 'error' value instead of list of meeting rooms
        self.assertTrue(meetings != 'error')

"""
Here some sample methods to call in other apps,
projects to do some syncing functions.

Like updating records of meetings, update logs and ...
"""
import logging
import datetime

from .bbb import BigBlueButton
from .models import Meeting, MeetingLog, MeetingRecord


def update_meetings_logs():
    """ Will iterate on all meetings, and check if they are closed,
    will close meetingLogs joined to them.
    """
    logging.info('[+] Check meetings and close left out meetingLogs.')

    meetings = Meeting.objects.all()
    for meeting in meetings:
        try:
            is_running = meeting.check_is_running(commit=True)
            if not is_running:
                now_date = datetime.datetime.now()
                MeetingLog.objects.filter(
                    meeting__meeting_id=meeting.meeting_id,
                    left_date__isnull=True
                ).update(left_date=now_date)
        except Exception as e:
            logging.error(str(e))
    logging.info('[+] Done checking meetings and updating logs for them.')


def update_meetings_records():
    """
    Will iterate on meetings,
    check if new record is created for them by bbb,
    then save it in database for showing to customers.
    """

    logging.info('[+] Checking meetings and store new records if created any!')

    meetings = Meeting.objects.all()
    for meeting in meetings:
        try:
            bbb = BigBlueButton()
            recordings = bbb.get_meeting_records(meeting.meeting_id)
            for record in recordings:
                """ record sample:
                {
                    'url': 'https://meeting.cpol.co/playback/presentation/2.0/playback.html?meetingId=0c19812ecd8955d77a3351a4e489fe50afcc-1612087443063',
                    'name': 'name of meeting',
                    'end_time': 1612099936637,
                    'raw_size': 165691706,
                    'record_id': '0c19812ecd8955d77a3351a4e489fe50afcc-1612087443063',
                    'meeting_id': 'meeting-id',
                    'start_time': 1612087443063,
                }
                """
                MeetingRecord.objects.get_or_create(
                    link=record['url'],
                    name=record['name'],
                    record_id=record['record_id'],
                    meeting=meeting,
                )
        except Exception as e:
            logging.error(str(e))

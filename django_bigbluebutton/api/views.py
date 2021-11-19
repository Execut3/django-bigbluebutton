import datetime
import json
import logging
import urllib.parse

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ..models import Meeting, MeetingLog
from .serializers import MeetingSerializer


class MeetingViewSet(ModelViewSet):
    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer

    @action(methods=['post'], detail=True, url_path='callback')
    def hook_callback(self, request, **kwargs):
        """ Data sample:
        event=%5B%7B%22data%22%3A%7B%22type%22%3A%22event%22%2C%22id%22%3A%22meeting-ended%22%2C%22attributes%22%3A%7B%22meeting%22%3A%7B%22internal-meeting-id%22%3A%2200834d44d223918856f4683db2fc2651dd05782e-1607608335199%22%2C%22external-meeting-id%22%3A%22testmeeting-11%22%7D%7D%2C%22event%22%3A%7B%22ts%22%3A1607608642899%7D%7D%7D%5D&timestamp=1607608642905&domain=meeting.cpol.co

        first should be url-decode to be like below:
            event=[
               {
                  "data":{
                     "type":"event",
                     "id":"user-emoji-changed",
                     "attributes":{
                        "meeting":{
                           "internal-meeting-id":"5c13f0e2e59b3348767e88ee9e7d8ee858689f8c-1607594986040",
                           "external-meeting-id":"meeting-11"
                        },
                        "user":{
                           "internal-user-id":"w_fqxudq3emu8z",
                           "external-user-id":"w_fqxudq3emu8z"
                        }
                     },
                     "event":{
                        "ts":1607595086800
                     }
                  }
               }
            ]&timestamp=1607608642905&domain=meeting.cpol.co
        """
        print('here')
        event_data = request.data.get('event', '')
        current_datetime = datetime.datetime.now()

        try:
            tmp = urllib.parse.unquote(event_data)
            event_data = json.loads(tmp)
            print(event_data)
            for e in event_data:
                e = e['data']
                event_id = e['id']
                if event_id in ['user-joined', 'user-left']:
                    try:
                        attributes = e['attributes']
                        meeting_id = attributes['meeting']['external-meeting-id']
                        user_id = attributes['user']['external-user-id']

                        try:
                            user_id_valid = int(user_id)
                        except:
                            user_id_valid = None

                        if not user_id_valid:
                            continue

                        from django_bigbluebutton.models import Meeting
                        meeting = Meeting.objects.filter(meeting_id=meeting_id).first()
                        if not meeting:
                            continue

                        # When user-joined/left is received
                        # By default we should set current date
                        # To all logs of this user which are null yet
                        MeetingLog.objects.filter(
                            meeting=meeting,
                            user_id=user_id_valid,
                            left_date__isnull=True
                        ).update(
                            left_date=current_datetime
                        )

                        if event_id == 'user-joined':
                            MeetingLog.objects.create(
                                meeting=meeting,
                                user_id=user_id_valid
                            )
                    except Exception as e:
                        logging.error(str(e))
                elif event_id == 'meeting-ended':
                    try:
                        attributes = e['attributes']
                        meeting_id = attributes['meeting']['external-meeting-id']

                        from django_bigbluebutton.models import Meeting
                        meeting = Meeting.objects.filter(meeting_id=meeting_id).first()
                        if not meeting:
                            continue

                        # Now bulk update all meetingLogs which their left_date is null
                        MeetingLog.objects.filter(
                            meeting=meeting,
                            left_date__isnull=True
                        ).update(
                            left_date=current_datetime
                        )
                    except Exception as e:
                        logging.error(str(e))

        except Exception as e:
            print(e)
            pass

        return Response({})

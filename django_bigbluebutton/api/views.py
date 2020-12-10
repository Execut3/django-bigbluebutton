from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from ..models import Meeting, MeetingLog
from .serializers import MeetingSerializer


class MeetingViewSet(ModelViewSet):
    queryset = Meeting.objects.all().prefetch_related('user', 'meeting')
    serializer_class = MeetingSerializer

    @action(methods=['post'], detail=True, url_path='callback')
    def hook_callback(self, request, **kwargs):
        print('here')

        return Response({})

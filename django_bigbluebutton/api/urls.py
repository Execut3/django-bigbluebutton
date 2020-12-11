from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import *

router = DefaultRouter()
router.register("meeting", MeetingViewSet, "meeting_vs")

urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import path, include

urlpatterns = [
    path("api/", include(("django_bigbluebutton.api.urls", "django_bigbluebutton.api.urls"), "api_bbb"), ),
]

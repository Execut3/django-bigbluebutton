from django.apps import AppConfig


class BigBlueButtonAppConfig(AppConfig):
    name = 'django_bigbluebutton'

    def ready(self):
        import django_bigbluebutton.signals


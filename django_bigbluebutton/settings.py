from django.conf import settings


# BBB_API_URL = getattr(settings, 'BBB_API_URL', None)
# BBB_SECRET_KEY = getattr(settings, 'BBB_SECRET_KEY', None)

# If UPDATE_RUNNING_ON_EACH_CALL=True, means that on each call of queryset for
# example gettings list of meetings and ..., call getMeetings from bigbluebutton
# And udpate status of each meetings. So sync local database Meetings is_running
# variable with getMeetings() output from bigbluebutton APIs.
# If UPDATE_RUNNING_ON_EACH_CALL=False, skip and only update is_running status
# when Refresh Meeting action is called from django admin.
UPDATE_RUNNING_ON_EACH_CALL = getattr(settings, 'UPDATE_RUNNING_ON_EACH_CALL', True)

from django.conf import settings


""" Below two variables are really important and should be set in project!"""
BBB_API_URL = getattr(settings, 'BBB_API_URL', None)
BBB_SECRET_KEY = getattr(settings, 'BBB_SECRET_KEY', None)


""" UPDATE_RUNNING_ON_EACH_CALL:

If UPDATE_RUNNING_ON_EACH_CALL=True, means that on each call of queryset for
example getting list of meetings and ..., call getMeetings from bigbluebutton
And update status of each meetings. So sync local database Meetings is_running
variable with getMeetings() output from bigbluebutton APIs.
If UPDATE_RUNNING_ON_EACH_CALL=False, skip and only update is_running status
when Refresh Meeting action is called from django admin.
"""
UPDATE_RUNNING_ON_EACH_CALL = getattr(settings, 'UPDATE_RUNNING_ON_EACH_CALL', True)


""" Other default variables for each meeting """
BBB_MAX_PARTICIPANTS = getattr(settings, 'BBB_MAX_PARTICIPANTS', 10)
BBB_WELCOME_TEXT = getattr(settings, 'BBB_WELCOME_TEXT', 'Welcome to meeting')
BBB_LOGOUT_URL = getattr(settings, 'BBB_LOGOUT_URL', BBB_API_URL)
BBB_RECORD = getattr(settings, 'BBB_RECORD', True)
BBB_AUTO_RECORDING = getattr(settings, 'BBB_AUTO_RECORDING', False)
BBB_ALLOW_START_STOP_RECORDING = getattr(settings, 'BBB_ALLOW_START_STOP_RECORDING', True)
BBB_WEBCAM_ONLY_FOR_MODS = getattr(settings, 'BBB_WEBCAM_ONLY_FOR_MODS', False)
BBB_LOCK_SETTINGS_DISABLE_CAM = getattr(settings, 'BBB_LOCK_SETTINGS_DISABLE_CAM', False)
BBB_LOCK_SETTINGS_DISABLE_MIC = getattr(settings, 'BBB_LOCK_SETTINGS_DISABLE_MIC', False)
BBB_LOCK_SETTINGS_DISABLE_PRIVATE_CHAT = getattr(settings, 'BBB_LOCK_SETTINGS_DISABLE_PRIVATE_CHAT', False)
BBB_LOCK_SETTINGS_DISABLE_PUBLIC_CHAT = getattr(settings, 'BBB_LOCK_SETTINGS_DISABLE_PUBLIC_CHAT', False)
BBB_LOCK_SETTINGS_DISABLE_NOTE = getattr(settings, 'BBB_LOCK_SETTINGS_DISABLE_NOTE', False)
BBB_LOCK_SETTINGS_LOCKED_LAYOUT = getattr(settings, 'BBB_LOCK_SETTINGS_LOCKED_LAYOUT', False)


# django-bigbluebutton

A Django Application for better interaction of Django projects with Big Blue Button APIs.

Features:

- Create room on BBB and store meeting info in a model for later access
- Start a meeting
- End a meeting
- Create join link for a meeting with moderator or normal access
- Get meeting report (activity of users in meeting and time log of them)
- Log each meeting for later access and reportings
- Create and Delete API Hook on BBB. (Will be usefull for example to be notified when user is leaved room from BBB and get noticed in your local service)

### Requirements

To use django-bigbluebutton followingpackages are needed. If you don't have them installed, they will be installed automatically.
```
Django>=2.0
requests>=2.0
```

### Installation

**Note:** This package is well tested on `django>=2.0`. But if you are using older versions can be
used with minor changes in structure.

install using pip:
```bash
pip install django-bigbluebutton
```

### Usage
Register app in `settings.py`

```python
INSTALLED_APPS = [
    "django_bigbluebutton",
]
```

Now should define you Big Blue Button Server core configs in `settings.py`:

```python
BBB_API_URL = 'https://test.com/bigbluebutton/api/'
BBB_SECRET_KEY = 'abcdefgabcdefgabcdefgabcdefgabcdefg'
```

Next Apply migrations:
```bash
python manage.py migrate
```

And finally run test:

```bash
python manage.py test
```

You can follow `tests.py` file to see how to use this package.


### Admin Integration

By installing this app in your django project, A admin section will be added named `Meeting`.
Under this section you can see list of open meetings, join meeting, create join link for other
users with moderator or attendee permissions.

Also to enable update state of each meeting (sync with bigbluebutton) set below variable in 
`settings.py`:

```python
UPDATE_RUNNING_ON_EACH_CALL = True
```

So whenever you open list of meetings in django admin, it will update state of all meetings in database
with result of `getMeetings` API from bigbluebutton.

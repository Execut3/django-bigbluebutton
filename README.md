# django-bigbluebutton

A Django Application for better interaction of Django projects with Big Blue Button APIs.

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

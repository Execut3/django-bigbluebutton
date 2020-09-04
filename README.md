# django-bigbluebutton

A Django Application for better interaction of Django projects with Big Blue Button APIs.

### Requirements

To use this package following needed. if not provided will be installed automatically.
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

Next apply migrations:
```bash
python manage.py migrate
```

And finally run test:

```bash
python manage.py test
```

You can follow `tests.py` file to see how to use this package.

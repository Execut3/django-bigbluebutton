import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

setup(
    name='django-bigbluebutton',
    version='0.5.9',
    packages=['django_bigbluebutton'],
    description='A Django APP to Integrate BigBlueButton APIs with your current Project',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Execut3',
    author_email='execut3.binarycodes@gmail.com',
    url='https://github.com/Execut3/django-bigbluebutton',
    license='GPT',
    install_requires=[
        'Django>=2.0',
        'requests>=2.0',
        'djangorestframework>=3.0.0'
    ],
    include_package_data=True,
)

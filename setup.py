
# -*- coding: utf-8 -*-
from setuptools import setup

import codecs

with codecs.open('README.md', encoding="utf-8") as fp:
    long_description = fp.read()
INSTALL_REQUIRES = [
    'apiflask~=0.10',
    'flask-sqlalchemy~=2.5',
    'flask-wtf~=0.15',
    'flask-login~=0.5',
    'bootstrap-flask~=2.0',
    'flask-compress~=1.10',
    'wtforms-sqlalchemy~=0.3',
    'flask~=2.0',
    'marshmallow-sqlalchemy>=0.27.0',
]

setup_kwargs = {
    'name': 'Djask',
    'version': '0.3.1',
    'description': 'An enhanced django-like Flask',
    'long_description': long_description,
    'license': 'MIT',
    'author': '',
    'author_email': 'andyzhou <andyforever0108@outlook.com>',
    'maintainer': None,
    'maintainer_email': None,
    'url': '',
    'packages': [
        'djask',
        'djask.auth',
        'djask.db',
        'djask.admin',
        'djask.admin.api',
    ],
    'package_dir': {'': 'src'},
    'package_data': {'': ['*']},
    'long_description_content_type': 'text/markdown',
    'keywords': ['flask', 'apiflask'],
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
    ],
    'install_requires': INSTALL_REQUIRES,
    'python_requires': '>=3.7',

}


setup(**setup_kwargs)


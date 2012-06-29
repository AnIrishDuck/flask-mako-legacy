"""
Flask-Mako
-------------

Add support for Mako templates to the Flask microframework.

"""
from setuptools import setup

setup(
    name='Flask-Mako',
    version='1.0',
    url='www.github.com/flask-mako',
    license='MIT',
    author='Frank Murphy',
    author_email='fmurphy@arbor.net',
    description='Adds Mako templating support to Flask',
    long_description=__doc__,
    py_modules=['flask'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

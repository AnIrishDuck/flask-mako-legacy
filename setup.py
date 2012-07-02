"""
Flask-Mako
-------------

Add support for Mako templates to the Flask microframework.

"""
from setuptools import setup

setup(
    name='Flask-Mako',
    version='0.1',
    url='https://github.com/AnIrishDuck/flask-mako',
    license='MIT',
    author='Frank Murphy',
    author_email='fpmurphy@mtu.edu',
    description='Adds Mako templating support to Flask',
    long_description=__doc__,
    py_modules=['flask_mako', 'test_flask_mako'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask', 'mako'
    ],
    test_suite='test_flask_mako.suite',
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

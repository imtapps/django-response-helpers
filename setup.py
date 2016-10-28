from distutils.core import setup
from setuptools import find_packages


setup(
    name="django-response-helpers",
    version='2.0.0',
    author="Aaron Madison",
    author_email="aaron.l.madison@gmail.com",
    description="A helper application for working with Django Responses",
    long_description=open('README.txt', 'r').read(),
    url="https://github.com/imtapps/django-response-helpers",
    packages=find_packages(exclude=['example']),
    install_requires=open('requirements/dist.txt').read().split("\n"),
    tests_require=open('requirements/ci.txt').read().split("\n"),
    zip_safe=False,
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
)


from setuptools import setup
from response_helpers import VERSION

REQUIREMENTS = [
    'django',
    'xhtml2pdf',
]
TEST_REQUIREMENTS = REQUIREMENTS + [
    'mock',
]


setup(
    name="django-response-helpers",
    version=VERSION,
    author="Aaron Madison",
    author_email="aaron.l.madison@gmail.com",
    description="A helper application for working with Django Responses",
    long_description=open('README.txt', 'r').read(),
    url="https://github.com/imtapps/django-response-helpers",
    packages=("response_helpers",),
    install_requires=REQUIREMENTS,
    tests_require=TEST_REQUIREMENTS,
    test_suite='runtests.runtests',
    zip_safe=False,
    classifiers = [
        "Development Status :: 3 - Alpha",
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

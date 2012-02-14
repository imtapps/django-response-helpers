
import os
import re
from distutils.core import Command, setup
from setuptools import find_packages

from response_helpers import VERSION

REQUIREMENTS = [
    'django',
]

TEST_REQUIREMENTS = [
    'mock>=0.8.0',
    'django-jenkins',
    'pep8',
    'pyflakes',
    'xhtml2pdf',
]

def do_setup():
    setup(
        name="django-response-helpers",
        version=VERSION,
        author="Aaron Madison",
        author_email="aaron.l.madison@gmail.com",
        description="A helper application for working with Django Responses",
        long_description=open('README.txt', 'r').read(),
        url="https://github.com/imtapps/django-response-helpers",
        packages=find_packages(exclude=['example']),
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
        cmdclass={
            'install_dev':InstallDependencies,
        }
    )

class InstallDependencies(Command):
    """
    Command to install both develop dependencies and test dependencies.

    Not sure why we can't find a built in command to do that already
    in an accessible way.
    """

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def get_test_dependencies(self):
        """
        replace all > or < in the dependencies so the system does not
        try to redirect stdin or stdout from/to a file.
        """
        command_line_deps = ' '.join(TEST_REQUIREMENTS)
        return re.sub(re.compile(r'([<>])'), r'\\\1', command_line_deps)

    def run(self):
        os.system("pip install ./")
        os.system("pip install %s" % self.get_test_dependencies())

if __name__ == '__main__':
    do_setup()

import shutil
import logging
import os
from django import test
from django.conf import settings
from django.test.utils import override_settings
from response_helpers.helpers import render_to_pdf


class PisaLoggingTests(test.TestCase):

    def setUp(self):
        self.log_path = '/tmp/asdf.log'

    def tearDown(self):
        self.cleanUpLogs()

    def cleanUpLogs(self):
        try:
            os.remove(self.log_path)
        except:
            pass

    def test_logs_raw_html_to_file(self):
        results = render_to_pdf('test.html', {'items': range(1)})
        with open(self.log_path) as g:
            output = g.read()
        self.assertIn('<h1>Hi</h1>', output)
